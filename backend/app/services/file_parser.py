"""File parser service for bank statement imports (CSV, OFX, PDF)."""

import csv
import io
import re
import unicodedata
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Any

from app.utils.logger import logger


BANK_DETECTION_RULES: list[tuple[list[str], str]] = [
    (["nubank", "nu pagamentos", "agencia 0001 conta"], "Nubank"),
    (["bradesco", "banco bradesco"], "Bradesco"),
    (["itau", "itau unibanco"], "Itau"),
    (["santander", "banco santander"], "Santander"),
    (["caixa", "caixa economica", "caixa economica federal", "cef"], "Caixa"),
    (["mercado pago", "mercadopago", "mercado livre", "mercadolivre"], "Mercado Pago"),
    (["pagbank", "pag seguro", "pagseguro"], "PagSeguro"),
    (["sicoob", "sicoob cocred", "sicoob credicitrus"], "Sicoob"),
    (["sicredi"], "Sicredi"),
    (["banco inter", "inter pagamentos", "inter"], "Inter"),
    (["c6 bank", "bco c6", "banco c6", "c6"], "C6 Bank"),
    (["banco do brasil"], "Banco do Brasil"),
]

CSV_ENCODING_CANDIDATES = ("utf-8-sig", "utf-8", "cp1252", "latin-1")
CSV_DELIMITERS = (",", ";", "\t", "|")


def _normalize_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", (value or "").strip().lower())
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def _detect_bank_name_from_text(value: str) -> str | None:
    normalized_text = _normalize_key(value or "").replace("_", " ").replace("-", " ")
    normalized_text = re.sub(r"\s+", " ", normalized_text).strip()

    for aliases, bank_name in BANK_DETECTION_RULES:
        if any(alias in normalized_text for alias in aliases):
            return bank_name

    if re.match(r"^nu\s", normalized_text):
        return "Nubank"
    if re.match(r"^mp\s", normalized_text):
        return "Mercado Pago"

    return None


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
        compact = raw[:8]
        try:
            return datetime.strptime(compact, "%Y%m%d").strftime("%Y-%m-%d")
        except ValueError:
            return compact

    for fmt in [
        "%d/%m/%Y",
        "%d/%m/%y",
        "%d-%m-%Y",
        "%Y-%m-%d",
        "%d.%m.%Y",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
    ]:
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


def _read_text_with_fallbacks(file_path: str) -> str:
    with open(file_path, "rb") as fh:
        raw = fh.read()

    for encoding in CSV_ENCODING_CANDIDATES:
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue

    return raw.decode("utf-8", errors="ignore")


def _sniff_csv_dialect(csv_text: str) -> csv.Dialect:
    sample = "\n".join(line for line in csv_text.splitlines()[:10] if line.strip())
    try:
        return csv.Sniffer().sniff(sample, delimiters="".join(CSV_DELIMITERS))
    except csv.Error:
        class FallbackDialect(csv.Dialect):
            delimiter = ";"
            quotechar = '"'
            escapechar = None
            doublequote = True
            skipinitialspace = True
            lineterminator = "\n"
            quoting = csv.QUOTE_MINIMAL

        if sample:
            counts = {delimiter: sample.count(delimiter) for delimiter in CSV_DELIMITERS}
            FallbackDialect.delimiter = max(counts, key=counts.get) if any(counts.values()) else ";"
        return FallbackDialect


def _normalize_csv_text(csv_text: str) -> str:
    lines = csv_text.splitlines()
    normalized_lines: list[str] = []
    for index, line in enumerate(lines):
        stripped = line.strip()
        if index == 0 and stripped.lower().startswith("sep="):
            continue
        normalized_lines.append(line)
    return "\n".join(normalized_lines)


def _extract_csv_transaction_block(csv_text: str) -> str:
    lines = csv_text.splitlines()
    if not lines:
        return csv_text

    def _score_header(line: str) -> int:
        normalized_headers = [_normalize_key(part) for part in re.split(r"[;,\t|]", line) if part.strip()]
        header_set = set(normalized_headers)

        date_aliases = {
            "date", "data", "transaction_date", "release_date", "dt_lancamento",
            "data_lancamento", "data_movimento", "dt",
        }
        description_aliases = {
            "description", "descricao", "historico", "memo", "detalhe", "complemento",
            "lancamento", "estabelecimento", "narrativa", "transaction_type", "type",
        }
        amount_aliases = {
            "amount", "valor", "vlr", "valor_rs", "valor_r$", "valor_liquido",
            "transaction_net_amount", "trnamt", "movimento", "credits", "debits",
        }

        score = 0
        if header_set & date_aliases:
            score += 2
        if header_set & description_aliases:
            score += 2
        if header_set & amount_aliases:
            score += 2
        if len(header_set) >= 3:
            score += 1
        return score

    best_index = 0
    best_score = -1
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        score = _score_header(stripped)
        if score > best_score:
            best_score = score
            best_index = index

    return "\n".join(lines[best_index:]).strip() if best_score >= 4 else csv_text


def _extract_bradesco_csv_transaction_block(csv_text: str) -> str:
    lines = csv_text.splitlines()
    if not lines:
        return csv_text

    start_index: int | None = None
    collected: list[str] = []

    for index, raw_line in enumerate(lines):
        line = raw_line.strip()
        normalized = _normalize_key(line)

        if start_index is None and normalized.startswith("data;lancamento;dcto.;credito (r$);debito (r$);saldo (r$)"):
            start_index = index
            collected.append(raw_line)
            continue

        if start_index is None:
            continue

        if "saldos invest facil" in normalized:
            break
        if normalized.startswith("data;lancamento;dcto.;credito (r$);debito (r$);saldo (r$)"):
            continue
        if normalized.startswith("total;"):
            continue
        if "ultimos lancamentos" in normalized:
            continue
        if not line:
            continue
        collected.append(raw_line)

    return "\n".join(collected).strip() if collected else csv_text


def _infer_amount_from_csv_row(normalized_row: dict[str, str]) -> str:
    amount = _pick(
        normalized_row,
        [
            "amount",
            "valor",
            "vlr",
            "valor rs",
            "valor r$",
            "valor liquido",
            "valor liquido r$",
            "valor líquido",
            "valor do lancamento",
            "valor do lancamento r$",
            "credito (r$)",
            "debito (r$)",
            "trnamt",
            "movimento",
            "transaction_net_amount",
        ],
    )
    debit = _pick(
        normalized_row,
        [
            "debito",
            "débito",
            "debito (r$)",
            "débito (r$)",
            "debito r$",
            "valor debito",
            "valor de debito",
            "saidas",
            "saída",
            "saida",
        ],
    )
    credit = _pick(
        normalized_row,
        [
            "credito",
            "crédito",
            "credito (r$)",
            "crédito (r$)",
            "credito r$",
            "valor credito",
            "valor de credito",
            "entradas",
            "entrada",
        ],
    )

    if (not amount or amount == "0") and (debit or credit):
        debit_val = float(_to_br_decimal(debit) or "0")
        credit_val = float(_to_br_decimal(credit) or "0")
        amount = str(credit_val - debit_val)

    normalized_amount = _to_br_decimal(amount)
    operation_hint = _normalize_key(_pick(
        normalized_row,
        ["type", "tipo", "natureza", "operacao", "operação", "dc", "movimento tipo"],
    )).lower()
    description_hint = _normalize_key(_pick(
        normalized_row,
        [
            "description",
            "descricao",
            "descrição",
            "historico",
            "histórico",
            "memo",
            "detalhe",
            "complemento",
            "lancamento",
            "lançamento",
            "estabelecimento",
            "narrativa",
            "transaction_type",
            "tipo_transacao",
        ],
    )).lower()

    if normalized_amount not in {"", "0"}:
        amount_float = float(normalized_amount)
        expense_hints = [
            "debito",
            "deb",
            "saida",
            "pagamento",
            "despesa",
            "cartao de credito",
            "cartao credito",
        ]
        income_hints = [
            "credito",
            "entrada",
            "receita",
            "recebimento",
        ]

        if amount_float > 0 and (
            any(token in operation_hint for token in expense_hints)
            or any(token in description_hint for token in ["pagamento de fatura"])
        ):
            return str(-amount_float)
        if amount_float < 0 and (
            any(token in operation_hint for token in income_hints)
            and "cartao de credito" not in operation_hint
            and "cartao credito" not in operation_hint
        ):
            return str(abs(amount_float))

    return normalized_amount


def _parse_pagseguro_pdf_lines(lines: list[str]) -> list[dict[str, Any]]:
    """Parse PagSeguro statement lines like: '20/07/2025 Pix recebido ... R$ 700,00'."""
    transactions: list[dict[str, Any]] = []
    line_pattern = re.compile(
        r"^(?P<date>\d{2}/\d{2}/\d{4})\s+(?P<desc>.+?)\s+(?P<sign>-?)R\$\s*(?P<amount>\d{1,3}(?:\.\d{3})*,\d{2})$",
        re.IGNORECASE,
    )
    balance_pattern = re.compile(
        r"^(?P<date>\d{2}/\d{2}/\d{4})\s+Saldo do dia\s+R\$\s*(?P<balance>\d{1,3}(?:\.\d{3})*,\d{2})$",
        re.IGNORECASE,
    )
    first_transaction_signed_amount: float | None = None
    first_transaction_date: str | None = None
    inferred_opening_balance: str | None = None
    first_balance_date: str | None = None

    for index, line in enumerate(lines):
        balance_match = balance_pattern.match(line.strip())
        if balance_match and first_transaction_signed_amount is not None and inferred_opening_balance is None:
            balance_value = float(_to_br_decimal(balance_match.group("balance")) or "0")
            opening_balance = balance_value - first_transaction_signed_amount
            inferred_opening_balance = f"{opening_balance:.2f}"
            first_balance_date = _normalize_date(balance_match.group("date"))
            continue

        match = line_pattern.match(line.strip())
        if not match:
            continue

        description = match.group("desc").strip()
        # Skip balance rows (not financial movements)
        if "saldo do dia" in description.lower():
            continue

        sign = "-" if match.group("sign") == "-" else ""
        amount = _to_br_decimal(f"{sign}{match.group('amount')}")
        signed_amount = float(amount or "0")
        normalized_date = _normalize_date(match.group("date"))

        if first_transaction_signed_amount is None:
            first_transaction_signed_amount = signed_amount
            first_transaction_date = normalized_date

        transactions.append(
            {
                "description": description[:250],
                "amount": amount,
                "date": normalized_date,
                "reference": f"pagseguro-pdf-{index + 1}",
            }
        )

    if inferred_opening_balance and first_balance_date:
        try:
            opening_date = (
                datetime.strptime(first_balance_date, "%Y-%m-%d").date() - timedelta(days=1)
            ).isoformat()
        except ValueError:
            opening_date = first_transaction_date or first_balance_date

        transactions.insert(
            0,
            {
                "description": "Saldo inicial inferido do extrato",
                "amount": inferred_opening_balance,
                "date": opening_date,
                "reference": f"pagseguro-opening-{opening_date}",
            },
        )

    return transactions


def detect_bank_name(file_path: str, file_type: str, original_filename: str | None = None) -> str | None:
    filename_bank = _detect_bank_name_from_text(original_filename or "")
    if filename_bank:
        return filename_bank

    normalized_name = _normalize_key(original_filename or "").replace("_", " ").replace("-", " ")
    if re.match(r"^nu\s", normalized_name):
        return "Nubank"
    if re.match(r"^mp\s", normalized_name):
        return "Mercado Pago"

    try:
        if str(file_type or "").lower() == "pdf":
            import pdfplumber

            with pdfplumber.open(file_path) as pdf:
                head_text = "\n".join((page.extract_text() or "") for page in pdf.pages[:2])
        else:
            with open(file_path, "rb") as fh:
                head_text = fh.read(12000).decode("utf-8", errors="ignore")
    except Exception:
        return None

    return _detect_bank_name_from_text(head_text)


PT_BR_MONTHS = {
    "JAN": 1,
    "FEV": 2,
    "MAR": 3,
    "ABR": 4,
    "MAI": 5,
    "JUN": 6,
    "JUL": 7,
    "AGO": 8,
    "SET": 9,
    "OUT": 10,
    "NOV": 11,
    "DEZ": 12,
}


def _normalize_ptbr_month_date(value: str) -> str:
    raw = re.sub(r"\s+", " ", str(value or "").strip().upper())
    match = re.match(r"^(?P<day>\d{2})\s+(?P<month>[A-ZÇ]{3})\s+(?P<year>\d{4})$", raw)
    if not match:
        return _normalize_date(value)

    month = PT_BR_MONTHS.get(match.group("month"))
    if not month:
        return _normalize_date(value)

    return f"{match.group('year')}-{month:02d}-{match.group('day')}"


def _infer_amount_sign(description: str, current_section: str | None, amount: str) -> str:
    normalized_amount = _to_br_decimal(amount)
    raw_amount = float(normalized_amount or "0")
    lower_desc = (description or "").lower()

    income_hints = [
        "transferência recebida",
        "transferencia recebida",
        "pix recebido",
        "recebimento",
        "depósito",
        "deposito",
        "estorno",
    ]
    expense_hints = [
        "transferência enviada",
        "transferencia enviada",
        "compra no débito",
        "compra no debito",
        "pagamento de boleto",
        "pagamento",
        "saque",
        "nupay",
    ]

    if any(hint in lower_desc for hint in income_hints):
        return str(abs(raw_amount))

    if any(hint in lower_desc for hint in expense_hints):
        return str(-abs(raw_amount))

    if current_section == "income":
        return str(abs(raw_amount))

    return str(-abs(raw_amount))


def _parse_nubank_pdf_lines(lines: list[str]) -> list[dict[str, Any]]:
    transactions: list[dict[str, Any]] = []
    current_date: str | None = None
    current_section: str | None = None

    date_total_pattern = re.compile(
        r"^(?P<date>\d{2}\s+[A-ZÇ]{3}\s+\d{4})\s+Total de\s+(?P<section>entradas|sa[ií]das)\s+[+-]\s*(?P<amount>\d{1,3}(?:\.\d{3})*,\d{2})$",
        re.IGNORECASE,
    )
    section_total_pattern = re.compile(
        r"^Total de\s+(?P<section>entradas|sa[ií]das)\s+[+-]\s*(?P<amount>\d{1,3}(?:\.\d{3})*,\d{2})$",
        re.IGNORECASE,
    )
    transaction_pattern = re.compile(
        r"^(?P<description>.+?)\s+(?P<amount>\d{1,3}(?:\.\d{3})*,\d{2})$"
    )

    ignore_contains = (
        "tem alguma dúvida?",
        "ouvidoria:",
        "extrato gerado dia",
        "valores em r$",
        "saldo inicial",
        "saldo final do período",
        "rendimento líquido",
        "movimentações",
    )

    ignore_prefixes = (
        "cpf ",
        "agência ",
        "agencia ",
        "conta",
        "jorge luis da silva borges",
    )

    for raw_line in lines:
        line = re.sub(r"\s+", " ", raw_line.strip())
        if not line:
            continue

        lower_line = line.lower()
        if any(token in lower_line for token in ignore_contains):
            continue
        if any(lower_line.startswith(prefix) for prefix in ignore_prefixes):
            continue
        if re.search(r"\b\d+\s+de\s+\d+\b", lower_line):
            continue

        date_total_match = date_total_pattern.match(line)
        if date_total_match:
            current_date = _normalize_ptbr_month_date(date_total_match.group("date"))
            current_section = "income" if "entrada" in date_total_match.group("section").lower() else "expense"
            continue

        section_total_match = section_total_pattern.match(line)
        if section_total_match and current_date:
            current_section = "income" if "entrada" in section_total_match.group("section").lower() else "expense"
            continue

        if not current_date:
            continue

        if "agência:" in lower_line or "agencia:" in lower_line or " conta:" in lower_line:
            continue
        if lower_line.startswith("/0001-") or lower_line.startswith("bco ") or lower_line.startswith("banco "):
            continue
        if re.match(r"^[a-z0-9 .()/-]+conta:\s*[\w-]+$", lower_line):
            continue

        transaction_match = transaction_pattern.match(line)
        if not transaction_match:
            continue

        description = transaction_match.group("description").strip(" -")
        amount = transaction_match.group("amount")

        if len(description) < 3:
            continue

        transactions.append(
            {
                "description": description[:250],
                "amount": _infer_amount_sign(description, current_section, amount),
                "date": current_date,
                "reference": None,
            }
        )

    return transactions


BRADESCO_TRANSACTION_LABELS = (
    "TRANSFERENCIA PIX",
    "PIX QR CODE ESTATIC",
    "PIX QR CODE ESTATICO",
    "PIX QR CODE DINAMICO",
    "PAGTO ELETRON COBRANCA",
    "TARIFA BANCARIA",
)


def _normalize_bradesco_pdf_line(line: str) -> str:
    return _normalize_key(re.sub(r"\s+", " ", str(line or "").strip()))


def _is_bradesco_pdf(lines: list[str]) -> bool:
    joined = "\n".join(_normalize_bradesco_pdf_line(line) for line in lines[:20])
    return "extrato de: ag:" in joined and "saldo (r$)" in joined


def _is_bradesco_stop_line(line: str) -> bool:
    normalized = _normalize_bradesco_pdf_line(line)
    return normalized.startswith("saldos invest facil")


def _is_bradesco_ignored_line(line: str) -> bool:
    if not line:
        return True

    normalized = _normalize_bradesco_pdf_line(line)
    ignored_prefixes = (
        "agencia",
        "extrato de:",
        "data lancamento",
        "ultimos lancamentos",
        "os dados acima",
        "data historico",
        "data historico valor",
        "saldos invest facil / plus",
    )
    if normalized.startswith(ignored_prefixes):
        return True
    if re.match(r"^\d{5}\s+\|\s+[\d-]+\s+\d{1,3}(?:\.\d{3})*,\d{2}\s+\d{1,3}(?:\.\d{3})*,\d{2}$", line):
        return True
    if re.match(r"^Total\s+", line):
        return True
    return False


def _is_bradesco_transaction_label(line: str) -> bool:
    normalized = _normalize_bradesco_pdf_line(line).upper()
    return any(normalized.startswith(label) for label in BRADESCO_TRANSACTION_LABELS)


def _dedupe_consecutive_parts(parts: list[str]) -> list[str]:
    normalized_parts: list[str] = []
    last_key = ""
    for part in parts:
        cleaned = re.sub(r"\s+", " ", str(part or "").strip())
        if not cleaned:
            continue
        key = cleaned.lower()
        if key == last_key:
            continue
        normalized_parts.append(cleaned)
        last_key = key
    return normalized_parts


def _dedupe_parsed_transactions(transactions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str]] = set()

    for item in transactions:
        key = (
            str(item.get("date") or ""),
            str(item.get("reference") or ""),
            str(item.get("amount") or ""),
            re.sub(r"\s+", " ", str(item.get("description") or "").strip()),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)

    return deduped


def _parse_bradesco_pdf_lines(lines: list[str]) -> list[dict[str, Any]]:
    transactions: list[dict[str, Any]] = []
    current_date: str | None = None
    pending_context: list[str] = []

    start_balance_pattern = re.compile(r"^(?P<date>\d{2}/\d{2}/\d{4})\s+SALDO ANTERIOR\b", re.IGNORECASE)
    transaction_line_pattern = re.compile(
        r"^(?:(?P<date>\d{2}/\d{2}/\d{4})\s+)?(?P<description>.*?)\s*(?P<reference>\d{1,10})\s+"
        r"(?P<amount>-?\d{1,3}(?:\.\d{3})*,\d{2})\s+(?P<balance>\d{1,3}(?:\.\d{3})*,\d{2})$"
    )

    i = 0
    while i < len(lines):
        line = re.sub(r"\s+", " ", lines[i].strip())
        if _is_bradesco_stop_line(line):
            break
        if _is_bradesco_ignored_line(line):
            i += 1
            continue

        start_balance_match = start_balance_pattern.match(line)
        if start_balance_match:
            current_date = _normalize_date(start_balance_match.group("date"))
            pending_context = []
            i += 1
            continue

        transaction_match = transaction_line_pattern.match(line)
        if transaction_match:
            line_date = transaction_match.group("date")
            if line_date:
                current_date = _normalize_date(line_date)
            if not current_date:
                i += 1
                continue

            description_parts = [part for part in pending_context if part]
            inline_description = re.sub(r"\s+", " ", transaction_match.group("description") or "").strip(" -")
            if inline_description:
                description_parts.append(inline_description)

            j = i + 1
            while j < len(lines):
                next_line = re.sub(r"\s+", " ", lines[j].strip())
                if _is_bradesco_stop_line(next_line):
                    break
                if _is_bradesco_ignored_line(next_line):
                    break
                if transaction_line_pattern.match(next_line):
                    break
                if _is_bradesco_transaction_label(next_line) and description_parts:
                    break
                description_parts.append(next_line)
                j += 1

            description = " ".join(_dedupe_consecutive_parts(description_parts)).strip() or "Transaction"
            transactions.append(
                {
                    "description": description[:250],
                    "amount": _to_br_decimal(transaction_match.group("amount")),
                    "date": current_date,
                    "reference": transaction_match.group("reference"),
                }
            )
            pending_context = []
            i = j
            continue

        pending_context.append(line)
        i += 1

    return _dedupe_parsed_transactions(transactions)


def parse_csv(file_path: str) -> list[dict[str, Any]]:
    """Parse CSV statements, including common Brazilian bank headers."""
    transactions: list[dict[str, Any]] = []
    csv_text = _normalize_csv_text(_read_text_with_fallbacks(file_path))
    is_bradesco_csv = (
        "extrato de: agencia:" in _normalize_key(csv_text[:500])
        and "lancamento;dcto.;credito (r$);debito (r$);saldo (r$)" in _normalize_key(csv_text)
    )
    if is_bradesco_csv:
        csv_text = _extract_bradesco_csv_transaction_block(csv_text)
    csv_text = _extract_csv_transaction_block(csv_text)
    dialect = _sniff_csv_dialect(csv_text)
    reader = csv.DictReader(io.StringIO(csv_text), dialect=dialect)
    for row in reader:
        normalized = {
            _normalize_key(k): str(v or "").strip()
            for k, v in row.items()
            if k
        }
        try:
            description = _pick(
                normalized,
                [
                    "description",
                    "descricao",
                    "descrição",
                    "historico",
                    "histórico",
                    "memo",
                    "detalhe",
                    "complemento",
                    "lancamento",
                    "lançamento",
                    "estabelecimento",
                    "narrativa",
                    "transaction_type",
                    "tipo_transacao",
                ],
            )
            raw_date_value = _pick(
                normalized,
                [
                    "date",
                    "data",
                    "transaction_date",
                    "release_date",
                    "dt_lancamento",
                    "dt lançamento",
                    "data lancamento",
                    "data lançamento",
                    "data movimento",
                    "dt",
                ],
            )
            amount = _infer_amount_from_csv_row(normalized)
            debit_value = _pick(
                normalized,
                [
                    "debito",
                    "débito",
                    "debito (r$)",
                    "débito (r$)",
                    "debito r$",
                ],
            )
            credit_value = _pick(
                normalized,
                [
                    "credito",
                    "crédito",
                    "credito (r$)",
                    "crédito (r$)",
                    "credito r$",
                ],
            )
            date_value = _normalize_date(
                raw_date_value
            )
            reference = _pick(
                normalized,
                [
                    "codigo da transacao",
                    "codigo transacao",
                    "codigo_da_transacao",
                    "codigo",
                    "código da transacao",
                    "código da transação",
                    "reference",
                    "ref",
                    "reference_id",
                    "documento",
                    "dcto.",
                    "dcto",
                    "doc",
                    "numero",
                    "n_documento",
                    "n documento",
                    "id",
                    "código",
                    "nsu",
                ],
            )
            normalized_description = _normalize_key(description)
            normalized_raw_date = _normalize_key(raw_date_value)

            if normalized_raw_date == "total" or normalized_description.startswith("total"):
                continue
            if "ultimos lancamentos" in normalized_description or "saldo invest facil" in normalized_description:
                continue

            if not any([description, amount not in {"", "0"}, date_value, reference]):
                continue

            if (
                str(amount).strip() in {"", "0", "0.0", "0.00"}
                and not debit_value
                and not credit_value
            ):
                continue

            transactions.append(
                {
                    "description": description[:250],
                    "amount": amount,
                    "date": date_value,
                    "reference": reference,
                }
            )
        except Exception as exc:
            logger.warning("Skipping CSV row due to error: %s", exc)
    if is_bradesco_csv:
        return _dedupe_parsed_transactions(transactions)
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

        if _is_bradesco_pdf(lines):
            bradesco_transactions = _parse_bradesco_pdf_lines(lines)
            if bradesco_transactions:
                return bradesco_transactions

        # Fast path for PagSeguro statements.
        if any("pagseguro" in ln.lower() for ln in lines):
            pagseguro_transactions = _parse_pagseguro_pdf_lines(lines)
            if pagseguro_transactions:
                return pagseguro_transactions

        # Fast path for Nubank account statements.
        if any("total de entradas +" in ln.lower() or "total de saídas -" in ln.lower() or "total de saidas -" in ln.lower() for ln in lines):
            nubank_transactions = _parse_nubank_pdf_lines(lines)
            if nubank_transactions:
                return nubank_transactions

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
