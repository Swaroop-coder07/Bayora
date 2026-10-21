"""A. Leakage Budget Engine.

MVP: prompt normalisation + lexical similarity + configurable threshold.
Advanced: pass `similarity_fn` backed by an embedding model (cosine similarity).
"""
import difflib
import re
import unicodedata
from dataclasses import dataclass
from typing import Callable, Iterable

STOPWORDS = {"a", "an", "the", "to", "of", "and", "or", "is", "are", "me", "you", "please", "your", "my", "i", "it"}


def normalize(text: str) -> str:
    t = unicodedata.normalize("NFKC", text).lower()
    t = re.sub(r"[^\w\s]", " ", t)
    return " ".join(w for w in t.split() if w not in STOPWORDS)


def similarity(a: str, b: str) -> float:
    na, nb = normalize(a), normalize(b)
    if not na or not nb:
        return 0.0
    sa, sb = set(na.split()), set(nb.split())
    jaccard = len(sa & sb) / len(sa | sb)
    sequence = difflib.SequenceMatcher(None, na, nb).ratio()
    return max(jaccard, sequence)


@dataclass
class BudgetResult:
    similar_count: int
    max_similarity: float
    risk_score: float
    budget_total: int
    budget_remaining: int
    level: str  # ok | warning | coarse | paused


def evaluate(
    prompt: str,
    recent_prompts: Iterable[str],
    threshold: float,
    budget_total: int,
    similarity_fn: Callable[[str, str], float] = similarity,
) -> BudgetResult:
    scores = [similarity_fn(prompt, p) for p in recent_prompts]
    count = sum(1 for s in scores if s >= threshold)
    remaining = max(0, budget_total - count)
    risk = round(min(1.0, count / budget_total), 2) if budget_total else 1.0

    if count >= budget_total:
        level = "paused"  # testing paused: model is not called
    elif remaining <= max(1, budget_total // 2):
        level = "coarse"  # detailed feedback downgraded to a coarse verdict
    elif count >= 1:
        level = "warning"
    else:
        level = "ok"
    return BudgetResult(count, round(max(scores, default=0.0), 2), risk, budget_total, remaining, level)
