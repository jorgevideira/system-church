"""File parser service for bank statement imports (CSV, OFX, PDF)."""

import csv
import re
import unicodedata
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any

from app.utils.logger import logger


def _normalize_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", (value or "").strip().lower())
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def _to_br_decimal(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        return "0"
    negative = any(token in raw.lower() for token in ["-", "(", "debito", "débito"])
    cleaned = re.sub(r"[^0-9,.-]", "", raw)

    if "," in cleaned and "." in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")

    if cleaned in {"", ".", "-"}:
        return "0"

    if negative and not cleaned.startswith("-"):
        cleaned = f"-{cleaned}"
    return cleaned


def _normalize_date(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""

    if re.match(r"^\d{8}", raw):
        return raw[:8]

    for fmt in ["%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y"]:
        try:
            parsed = datetime.strptime(raw, fmt)
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return raw


def _pick(normalized_row: dict[str, str], aliases: list[str], default: str = "") -> str:
    for alias in aliases:
        if alias in normalized_row and normalized_row[alias]:
            return normalized_row[alias]
    return default


def _parse_pagseguro_pdf_lines(lines: list[str]) -> list[dict[str, Any]]:
    """Parse PagSeguro statement lines like: '20/07/2025 Pix recebido ... R$ 700,00'."""
    transactions: list[dict[str, Any]] = []
    line_pattern = re.compile(
        r"^(?P<date>\d{2}/\d{2}/\d{4})\s+(?P<desc>.+?)\s+(?P<sign>-?)R\$\s*(?P<amount>\d{1,3}(?:\.\d{3})*,\d{2})$",
        re.IGNORECASE,
    )

    for line in lines:
        match = line_pattern.match(line.strip())
        if not match:
            continue

        description = match.group("desc").strip()
        # Skip balance rows (not financial movements)
        if "saldo do dia" in description.lower():
            continue

        sign = "-" if match.group("sign") == "-" else ""
        amount = _to_br_decimal(f"{sign}{match.group('amount')}")

        transactions.append(
            {
                "description": description[:250],
                "amount": amount,
                "date": _normalize_date(match.group("date")),
                "reference": None,
            }
        )

    return transactions


def parse_csv(file_path: str) -> list[dict[str, Any]]:
    """Parse CSV statements, including common Brazilian bank headers."""
    transactions: list[dict[str, Any]] = []
    with open(file_path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            normalized = {
                _normalize_key(k): str(v or "").strip()
                for k, v in row.items()
                if k
            }
            try:
                amount = _pick(
                    normalized,
                    ["amount", "valor", "vlr", "valor rs", "valor r$", "valor liquido"],
                )
                debit = _pick(normalized, ["debito", "débito", "saidas", "saida"])
                credit = _pick(normalized, ["credito", "crédito", "entradas", "entrada"])
                if (not amount or amount == "0") and (debit or credit):
                    debit_val = float(_to_br_decimal(debit) or "0")
                    credit_val = float(_to_br_decimal(credit) or "0")
                    amount = str(credit_val - debit_val)

                transactions.append(
                    {
                        "description": _pick(
                            normalized,
                            ["description", "descricao", "historico", "memo", "detalhe", "complemento"],
                        ),
                        "amount": _to_br_decimal(amount),
                        "date": _normalize_date(
                            _pick(normalized, ["date", "data", "transaction_date", "dt_lancamento", "dt"])
                        ),
                        "reference": _pick(
                            normalized,
                            ["reference", "ref", "documento", "doc", "numero", "n_documento", "id"],
                        ),
                    }
                )
            except Exception as exc:
                logger.warning("Skipping CSV row due to error: %s", exc)
    return transactions


def parse_ofx(file_path: str) -> list[dict[str, Any]]:
    """Parse OFX/QFX via ofxparse with XML fallback."""
    transactions: list[dict[str, Any]] = []
    try:
        from ofxparse import OfxParser

        with open(file_path, "rb") as fh:
            ofx = OfxParser.parse(fh)

        for account in getattr(ofx, "accounts", []) or []:
            for trn in getattr(account, "statement", []).transactions:
                transactions.append(
                    {
                        "description": (trn.memo or trn.payee or "").strip(),
                        "amount": str(trn.amount or 0),
                        "date": trn.date.strftime("%Y-%m-%d") if trn.date else "",
                        "reference": (trn.id or "").strip() or None,
                    }
                )
        if transactions:
            return transactions
    except Exception as exc:
        logger.warning("ofxparse failed for %s, trying XML fallback: %s", file_path, exc)

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        for stmttrn in root.iter("STMTTRN"):
            def _text(tag: str) -> str:
                el = stmttrn.find(tag)
                return el.text.strip() if el is not None and el.text else ""

            transactions.append(
                {
                    "description": _text("NAME") or _text("MEMO"),
                    "amount": _to_br_decimal(_text("TRNAMT")),
                    "date": _normalize_date(_text("DTPOSTED")[:8]),
                    "reference": _text("FITID"),
                }
            )
    except ET.ParseError as exc:
        logger.error("OFX parse error for %s: %s", file_path, exc)
    return transactions


def parse_pdf(file_path: str) -> list[dict[str, Any]]:
    """
    Parse PDF bank statements (especially Brazilian Bradesco format) by extracting
    text and parsing transaction lines with multi-line descriptions.
    """
    transactions: list[dict[str, Any]] = []
    try:
        import pdfplumber
    except Exception as exc:
        logger.error("pdfplumber not available for %s: %s", file_path, exc)
        return []

    try:
        with pdfplumber.open(file_path) as pdf:
            lines: list[str] = []
            for page in pdf.pages:
                text = page.extract_text() or ""
                page_lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
                lines.extend(page_lines)

        # Fast path for PagSeguro statements.
        if any("pagseguro" in ln.lower() for ln in lines):
            pagseguro_transactions = _parse_pagseguro_pdf_lines(lines)
            if pagseguro_transactions:
                return pagseguro_transactions

        date_prefix_pattern = re.compile(r"^(?P<date>\d{2}/\d{2}/\d{4})\s+(?P<rest>.*)$")
        entry_with_date_pattern = re.compile(
            r"^(?P<date>\d{2}/\d{2}/\d{4})\s+(?P<doc>\d{1,10})\s+(?P<amount>-?\d{1,3}(?:\.\d{3})*,\d{2})\s+(?P<balance>\d{1,3}(?:\.\d{3})*,\d{2})$"
        )
        entry_no_date_pattern = re.compile(
            r"^(?P<doc>\d{1,10})\s+(?P<amount>-?\d{1,3}(?:\.\d{3})*,\d{2})\s+(?P<balance>\d{1,3}(?:\.\d{3})*,\d{2})$"
        )

        ignore_starts = (
            "Agência",
            "Extrato de:",
            "Data Lançamento",
            "Últimos Lançamentos",
            "Saldos Invest Fácil",
            "Data Histórico",
        )

        current_date: str | None = None
        current_context = ""
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if not line:
                i += 1
                continue
            if line.startswith(ignore_starts):
                i += 1
                continue
            if "Total Disponível" in line or "Os dados acima" in line:
                i += 1
                continue
            if re.match(r"^Total\s+", line):
                i += 1
                continue

            date_match = date_prefix_pattern.match(line)
            if date_match:
                current_date = date_match.group("date")
                rest = date_match.group("rest").strip()
                upper_rest = rest.upper()
                if "SALDO ANTERIOR" in upper_rest or "SALDO INVEST" in upper_rest:
                    i += 1
                    continue

                with_date = entry_with_date_pattern.match(line)
                if with_date:
                    description_parts: list[str] = []
                    if current_context:
                        description_parts.append(current_context)
                    consumed = 0
                    if i + 1 < len(lines) and re.match(r"^(REM:|DES:)", lines[i + 1], re.IGNORECASE):
                        description_parts.append(lines[i + 1].strip())
                        consumed = 1

                    amount = with_date.group("amount")
                    desc = " ".join(description_parts).strip()
                    desc_lower = desc.lower()
                    amount_float = float(_to_br_decimal(amount))
                    if amount_float > 0 and any(tok in desc_lower for tok in ["des:", "tarifa", "pagto", "débito", "debito"]):
                        amount_float = -amount_float

                    transactions.append(
                        {
                            "description": (re.sub(r"\s+", " ", desc) or "Transaction")[:250],
                            "amount": str(amount_float),
                            "date": _normalize_date(current_date),
                            "reference": with_date.group("doc"),
                        }
                    )
                    current_context = ""
                    i += 1 + consumed
                    continue

                current_context = rest
                i += 1
                continue

            no_date = entry_no_date_pattern.match(line)
            if no_date and current_date:
                description_parts = []
                if current_context:
                    description_parts.append(current_context)
                consumed = 0
                if i + 1 < len(lines) and re.match(r"^(REM:|DES:)", lines[i + 1], re.IGNORECASE):
                    description_parts.append(lines[i + 1].strip())
                    consumed = 1

                amount = no_date.group("amount")
                desc = " ".join(description_parts).strip()
                desc_lower = desc.lower()
                amount_float = float(_to_br_decimal(amount))
                if amount_float > 0 and any(tok in desc_lower for tok in ["des:", "tarifa", "pagto", "débito", "debito"]):
                    amount_float = -amount_float

                transactions.append(
                    {
                        "description": (re.sub(r"\s+", " ", desc) or "Transaction")[:250],
                        "amount": str(amount_float),
                        "date": _normalize_date(current_date),
                        "reference": no_date.group("doc"),
                    }
                )
                current_context = ""
                i += 1 + consumed
                continue

            if not re.search(r"\d{1,3}(?:\.\d{3})*,\d{2}", line):
                current_context = line

            i += 1

    except Exception as exc:
        logger.error("PDF parse error for %s: %s", file_path, exc)
        return []

    if not transactions:
        logger.warning("PDF parsed but no transaction lines found in %s", file_path)
    return transactions


def parse_file(file_path: str, file_type: str) -> list[dict[str, Any]]:
    """Dispatch to the correct parser based on *file_type*."""
    dispatch = {
        "csv": parse_csv,
        "ofx": parse_ofx,
        "pdf": parse_pdf,
    }
    parser = dispatch.get(file_type.lower())
    if parser is None:
        logger.error("Unknown file type '%s'", file_type)
        return []
    return parser(file_path)
