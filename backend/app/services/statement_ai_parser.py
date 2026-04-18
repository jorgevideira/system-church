"""Optional Ollama-based fallback parser for bank statements."""

from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from typing import Any

import httpx

from app.core.config import settings
from app.services.ai_classifier import EXPENSE_HINTS, INCOME_HINTS
from app.services.file_parser import _normalize_date, _to_br_decimal
from app.utils.logger import logger


def is_enabled() -> bool:
    return bool(settings.OLLAMA_ENABLED and settings.OLLAMA_BASE_URL and settings.OLLAMA_MODEL)


def _extract_text(file_path: str, file_type: str) -> str:
    normalized_type = str(file_type or "").strip().lower()
    try:
        if normalized_type == "pdf":
            import pdfplumber

            parts: list[str] = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text() or ""
                    if text.strip():
                        parts.append(text)
            return "\n\n".join(parts).strip()

        with open(file_path, "rb") as fh:
            raw = fh.read()
        return raw.decode("utf-8", errors="ignore").strip() or raw.decode("latin-1", errors="ignore").strip()
    except Exception as exc:
        logger.warning("AI statement parser could not extract text from %s: %s", file_path, exc)
        return ""


def _build_prompt(raw_text: str, file_type: str) -> str:
    clipped_text = raw_text[:40000]
    return (
        "Você é um extrator de movimentações financeiras de extratos bancários brasileiros.\n"
        "Analise o conteúdo abaixo e devolva APENAS JSON válido.\n"
        "Formato obrigatório:\n"
        "{\n"
        '  "transactions": [\n'
        "    {\n"
        '      "date": "YYYY-MM-DD",\n'
        '      "description": "texto da movimentação",\n'
        '      "amount": "-123.45",\n'
        '      "reference": "opcional"\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "Regras:\n"
        "- Ignore cabeçalhos, saldos, totais, páginas e textos institucionais.\n"
        "- Uma linha por movimentação financeira real.\n"
        "- Use valor negativo para saída/débito e positivo para entrada/crédito.\n"
        "- Converta valores brasileiros para ponto decimal.\n"
        "- Se a data estiver ambígua, tente normalizar; se não der, omita a movimentação.\n"
        "- Não invente movimentações.\n"
        "- Não escreva markdown, explicações ou comentários.\n\n"
        f"Tipo do arquivo: {file_type}\n"
        "Conteúdo do extrato:\n"
        f"{clipped_text}"
    )


def _load_transactions_from_response(response_text: str) -> list[dict[str, Any]]:
    payload = json.loads(response_text)
    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict):
        items = payload.get("transactions") or []
    else:
        items = []

    transactions: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        description = str(item.get("description") or "").strip()
        date_value = _normalize_date(item.get("date"))
        amount_value = _to_br_decimal(item.get("amount"))
        reference = str(item.get("reference") or "").strip() or None
        if not description or not date_value:
            continue
        transactions.append(
            {
                "description": description[:250],
                "date": date_value,
                "amount": _normalize_amount_by_description(description, amount_value),
                "reference": reference,
            }
        )
    return transactions


def _normalize_amount_by_description(description: str, amount_value: str) -> str:
    lower_desc = (description or "").lower()
    try:
        amount = Decimal(str(amount_value or "0"))
    except (InvalidOperation, TypeError, ValueError):
        return str(amount_value or "0")

    if amount < 0 and any(hint in lower_desc for hint in INCOME_HINTS):
        return str(abs(amount))

    if amount > 0 and any(hint in lower_desc for hint in EXPENSE_HINTS):
        return str(-abs(amount))

    return str(amount)


def parse_statement_with_ollama(file_path: str, file_type: str) -> list[dict[str, Any]]:
    if not is_enabled():
        return []

    raw_text = _extract_text(file_path, file_type)
    if not raw_text:
        return []

    prompt = _build_prompt(raw_text, file_type)
    try:
        with httpx.Client(timeout=float(settings.OLLAMA_TIMEOUT_SECONDS)) as client:
            response = client.post(
                f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                },
            )
            response.raise_for_status()
            payload = response.json()
    except Exception as exc:
        logger.warning("Ollama fallback failed for %s: %s", file_path, exc)
        return []

    raw_response = str(payload.get("response") or "").strip()
    if not raw_response:
        return []

    try:
        transactions = _load_transactions_from_response(raw_response)
    except Exception as exc:
        logger.warning("Ollama returned invalid JSON for %s: %s", file_path, exc)
        return []

    logger.info("Ollama parsed %s transactions for %s", len(transactions), file_path)
    return transactions
