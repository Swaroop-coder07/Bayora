"""B. Canary Secret Tripwire.

MVP: exact match.  Advanced (also implemented): normalised matching that catches
case changes, spacing, punctuation and zero-width characters, with multiple canaries.
"""
import re
import unicodedata
from dataclasses import dataclass, field

_ZERO_WIDTH = re.compile("[\u200b-\u200f\u2060\ufeff]")
WITHHELD = "[RESPONSE WITHHELD: canary leak detected]"


def _norm(text: str) -> str:
    t = unicodedata.normalize("NFKC", text)
    t = _ZERO_WIDTH.sub("", t).lower()
    return re.sub(r"[^a-z0-9]", "", t)


@dataclass
class CanaryScan:
    exact: list = field(default_factory=list)       # indexes found verbatim (case-insensitive)
    obfuscated: list = field(default_factory=list)  # indexes found only after normalisation

    @property
    def hits(self) -> list:
        return sorted(set(self.exact) | set(self.obfuscated))

    @property
    def tripped(self) -> bool:
        return bool(self.hits)


def label(index: int) -> str:
    return f"CANARY-{index + 1}"


def scan(text: str, canaries: list) -> CanaryScan:
    result = CanaryScan()
    low, normed = text.lower(), _norm(text)
    for i, c in enumerate(canaries):
        if not c:
            continue
        if c.lower() in low:
            result.exact.append(i)
        elif _norm(c) and _norm(c) in normed:
            result.obfuscated.append(i)
    return result


def mask(text: str, canaries: list) -> str:
    """Returns text that is safe to show / store: the real secret never survives."""
    first = scan(text, canaries)
    if not first.tripped:
        return text
    masked = text
    for i in first.exact:
        masked = re.sub(re.escape(canaries[i]), f"[{label(i)} MASKED]", masked, flags=re.IGNORECASE)
    if scan(masked, canaries).tripped:  # obfuscated variant we cannot pinpoint -> withhold all
        return WITHHELD
    return masked
