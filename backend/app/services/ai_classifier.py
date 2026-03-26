"""Simple keyword-based AI transaction classifier (no external ML dependencies)."""

KEYWORD_MAP: dict[str, list[str]] = {
    "Tithes": ["tithe", "dízimo", "dizimo", "décimo", "decimo"],
    "Offerings": ["offering", "oferta", "donation", "doação", "doacao", "contribuição", "contribuicao"],
    "Missions": ["mission", "missão", "missao", "missionary", "missionário", "missionario", "outreach"],
    "Utilities": [
        "electricity", "energia", "luz", "water", "água", "agua", "internet", "phone", "telefone",
        "gas", "utility", "conta de",
    ],
    "Personnel": [
        "salary", "salário", "salario", "payroll", "folha", "staff", "employee", "funcionário",
        "funcionario", "wage", "contractor",
    ],
    "Maintenance": [
        "repair", "reparo", "maintenance", "manutenção", "manutencao", "cleaning", "limpeza",
        "renovation", "renovação", "renovacao", "fix",
    ],
    "Events": [
        "event", "evento", "conference", "conferência", "conferencia", "retreat", "retiro",
        "concert", "show", "worship", "culto",
    ],
    "Administrative": [
        "office", "escritório", "escritorio", "supplies", "material", "printing", "impressão",
        "impressao", "software", "subscription", "assinatura", "admin",
    ],
}

INCOME_HINTS = [
    "rem:", "receb", "credito", "crédito", "pix recebido", "deposito", "depósito",
    "oferta", "dizimo", "dízimo", "doacao", "doação", "contribuicao", "contribuição",
    "transferencia recebida", "transferência recebida",
]

EXPENSE_HINTS = [
    "des:", "pagto", "pagamento", "tarifa", "debito", "débito", "boleto",
    "conta", "manutencao", "manutenção", "compra", "saque", "pix enviado",
    "transferencia enviada", "transferência enviada",
]


def classify_transaction(
    description: str,
    categories: list[dict],
) -> tuple[str | None, float]:
    """Return (category_name, confidence) using keyword matching.

    *categories* is a list of dicts with at least a ``name`` key.
    Returns (None, 0.0) when no match is found.
    """
    lower_desc = description.lower()
    available_names = {c["name"] for c in categories}

    best_category: str | None = None
    best_score: float = 0.0

    for category_name, keywords in KEYWORD_MAP.items():
        if category_name not in available_names:
            continue
        for kw in keywords:
            if kw in lower_desc:
                # Simple scoring: longer keyword → higher confidence
                score = min(0.5 + len(kw) * 0.05, 0.95)
                if score > best_score:
                    best_score = score
                    best_category = category_name
                break

    return best_category, best_score


def infer_transaction_type(
    description: str,
    parsed_amount: float | None = None,
) -> tuple[str, float]:
    """Infer transaction type as (income|expense, confidence).

    Priority:
    1. Description hints (REM:/DES:/keywords)
    2. Parsed amount sign fallback
    3. Conservative default (expense)
    """
    lower_desc = (description or "").lower()

    for hint in INCOME_HINTS:
        if hint in lower_desc:
            return "income", 0.9

    for hint in EXPENSE_HINTS:
        if hint in lower_desc:
            return "expense", 0.9

    if parsed_amount is not None:
        if parsed_amount > 0:
            return "income", 0.65
        if parsed_amount < 0:
            return "expense", 0.65

    return "expense", 0.5
