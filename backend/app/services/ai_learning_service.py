"""Learning helpers to persist manual corrections and reuse them in classification."""

import re
import unicodedata
from collections import Counter
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models.classification_feedback import ClassificationFeedback
from app.db.models.category import Category

STOPWORDS = {
    "de", "da", "do", "das", "dos", "para", "com", "sem", "por", "em", "no", "na",
    "um", "uma", "o", "a", "e", "ou", "pix", "qr", "code", "ltda", "me",
}


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.lower()


def extract_keywords(description: str, max_keywords: int = 6) -> list[str]:
    normalized = _normalize(description)
    tokens = re.findall(r"[a-z0-9]{3,}", normalized)
    filtered = [t for t in tokens if t not in STOPWORDS]
    freq = Counter(filtered)
    return [kw for kw, _ in freq.most_common(max_keywords)]


def record_feedback(
    db: Session,
    *,
    tenant_id: int,
    user_id: int,
    description: str,
    category_id: Optional[int],
    transaction_type: Optional[str],
) -> None:
    keywords = extract_keywords(description)
    if not keywords:
        return

    for kw in keywords:
        rule = (
            db.query(ClassificationFeedback)
            .filter(
                ClassificationFeedback.tenant_id == tenant_id,
                ClassificationFeedback.user_id == user_id,
                ClassificationFeedback.keyword == kw,
                ClassificationFeedback.category_id == category_id,
                ClassificationFeedback.transaction_type == transaction_type,
            )
            .first()
        )
        if rule:
            rule.weight += 1
        else:
            db.add(
                ClassificationFeedback(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    keyword=kw,
                    category_id=category_id,
                    transaction_type=transaction_type,
                    weight=1,
                )
            )
    db.commit()


def infer_from_feedback(
    db: Session,
    *,
    tenant_id: int,
    user_id: int,
    description: str,
) -> tuple[Optional[str], Optional[str], float]:
    keywords = extract_keywords(description)
    if not keywords:
        return None, None, 0.0

    rules = (
        db.query(ClassificationFeedback)
        .filter(
            ClassificationFeedback.tenant_id == tenant_id,
            ClassificationFeedback.user_id == user_id,
            ClassificationFeedback.keyword.in_(keywords),
        )
        .all()
    )
    if not rules:
        return None, None, 0.0

    category_scores: dict[int, int] = {}
    type_scores: dict[str, int] = {}

    for rule in rules:
        if rule.category_id:
            category_scores[rule.category_id] = category_scores.get(rule.category_id, 0) + int(rule.weight or 0)
        if rule.transaction_type:
            type_scores[rule.transaction_type] = type_scores.get(rule.transaction_type, 0) + int(rule.weight or 0)

    category_name = None
    if category_scores:
        best_category_id = max(category_scores, key=category_scores.get)
        cat = db.query(Category).filter(Category.id == best_category_id, Category.tenant_id == tenant_id).first()
        if cat:
            category_name = cat.name

    tx_type = max(type_scores, key=type_scores.get) if type_scores else None

    total_weight = sum(r.weight for r in rules)
    confidence = min(0.55 + (total_weight * 0.03), 0.98)
    return category_name, tx_type, confidence
