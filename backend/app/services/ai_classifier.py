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
