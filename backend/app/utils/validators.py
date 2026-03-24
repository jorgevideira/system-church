"""Custom validators for Brazilian documents and financial amounts."""

import re
from decimal import Decimal, InvalidOperation


def validate_cpf(cpf: str) -> bool:
    """Validate a Brazilian CPF number (11 digits, with or without formatting)."""
    digits = re.sub(r"\D", "", cpf)
    if len(digits) != 11 or digits == digits[0] * 11:
        return False

    def _checksum(d: str, factor: int) -> int:
        total = sum(int(d[i]) * (factor - i) for i in range(factor - 1))
        remainder = (total * 10) % 11
        return 0 if remainder >= 10 else remainder

    return _checksum(digits, 10) == int(digits[9]) and _checksum(digits, 11) == int(digits[10])


def validate_cnpj(cnpj: str) -> bool:
    """Validate a Brazilian CNPJ number (14 digits, with or without formatting)."""
    digits = re.sub(r"\D", "", cnpj)
    if len(digits) != 14 or digits == digits[0] * 14:
        return False

    def _checksum(d: str, weights: list[int]) -> int:
        total = sum(int(d[i]) * weights[i] for i in range(len(weights)))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder

    w1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    w2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    return _checksum(digits, w1) == int(digits[12]) and _checksum(digits, w2) == int(digits[13])


def validate_amount(amount) -> bool:
    """Return True if *amount* is a positive number."""
    try:
        return Decimal(str(amount)) > 0
    except (InvalidOperation, TypeError):
        return False


def sanitize_string(value: str) -> str:
    """Strip leading/trailing whitespace and collapse internal whitespace."""
    return re.sub(r"\s+", " ", value).strip()
