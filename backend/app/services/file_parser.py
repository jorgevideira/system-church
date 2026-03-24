"""File parser service for bank statement imports (CSV, OFX, PDF)."""

import csv
import xml.etree.ElementTree as ET
from datetime import date
from typing import Any

from app.utils.logger import logger


def parse_csv(file_path: str) -> list[dict[str, Any]]:
    """Parse a CSV bank statement.

    Expected columns (case-insensitive): description, amount, date, reference.
    """
    transactions: list[dict[str, Any]] = []
    with open(file_path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            # Normalise keys to lower-case without surrounding whitespace
            normalised = {k.strip().lower(): v.strip() for k, v in row.items()}
            try:
                transactions.append(
                    {
                        "description": normalised.get("description") or normalised.get("memo", ""),
                        "amount": normalised.get("amount", "0"),
                        "date": normalised.get("date") or normalised.get("transaction_date", ""),
                        "reference": normalised.get("reference") or normalised.get("ref"),
                    }
                )
            except Exception as exc:
                logger.warning("Skipping CSV row due to error: %s", exc)
    return transactions


def parse_ofx(file_path: str) -> list[dict[str, Any]]:
    """Parse a basic OFX/QFX file (XML dialect)."""
    transactions: list[dict[str, Any]] = []
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
                    "amount": _text("TRNAMT"),
                    "date": _text("DTPOSTED")[:8],  # YYYYMMDD
                    "reference": _text("FITID"),
                }
            )
    except ET.ParseError as exc:
        logger.error("OFX parse error for %s: %s", file_path, exc)
    return transactions


def parse_pdf(file_path: str) -> list[dict[str, Any]]:
    """Placeholder for PDF bank statement parsing.

    A real implementation would use pdfplumber or pypdf.
    """
    logger.warning("PDF parsing is not yet implemented for %s", file_path)
    return []


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
