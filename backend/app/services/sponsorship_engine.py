"""
Sponsorship Detection Engine
Analyzes job description text to determine H1B / visa sponsorship availability.
"""
import re
from typing import Tuple
from app.models.models import SponsorshipStatus


# ─── Signal lists ─────────────────────────────────────────────────────────────

# Patterns that indicate sponsorship is AVAILABLE (boost)
SPONSORSHIP_POSITIVE_PATTERNS = [
    r"\bh[\-\s]?1[\-\s]?b\s+(?:visa\s+)?(?:sponsorship|transfer|supported|available|provided|welcome)\b",
    r"\bvisa\s+sponsorship\b",
    r"\bsponsor(?:ship|ed|ing)?\s+(?:visa|work\s+authorization|h1b|h-1b)\b",
    r"\bwill\s+(?:sponsor|support|provide)\s+(?:visa|work\s+auth|h1b)\b",
    r"\bimmigration\s+(?:support|assistance|sponsorship)\b",
    r"\bopen\s+to\s+(?:visa\s+)?sponsorship\b",
    r"\bh1b\s+transfer\s+(?:ok|accepted|welcome|considered)\b",
    r"\bwork\s+authorization\s+(?:provided|sponsored|supported)\b",
    r"\bopen\s+to\s+all\s+(?:work\s+)?authorizations?\b",
    r"\bsponsor(?:ship)?\s+available\b",
]

# Patterns that indicate sponsorship is NOT available (downrank/exclude)
SPONSORSHIP_NEGATIVE_PATTERNS = [
    r"\bno\s+(?:visa\s+)?sponsorship\b",
    r"\bwill\s+not\s+(?:sponsor|provide\s+sponsorship)\b",
    r"\bnot\s+(?:able|eligible)\s+to\s+(?:sponsor|provide\s+sponsorship)\b",
    r"\bsponsorship\s+(?:is\s+)?not\s+(?:available|offered|provided)\b",
    r"\bauthorized\s+to\s+work\s+(?:in\s+the\s+us\s+)?without\s+(?:visa\s+)?sponsorship\b",
    r"\bmust\s+(?:be\s+)?(?:a\s+)?(?:us\s+)?(?:citizen|permanent\s+resident)\b",
    r"\bus\s+citizen(?:ship)?\s+(?:only|required)\b",
    r"\bsecurity\s+clearance\s+required\b",
    r"\bclearance\s+(?:required|mandatory|needed)\b",
    r"\bactive\s+(?:security\s+)?clearance\b",
    r"\bts(?:[\s\/]sci)?\s+clearance\b",
    r"\bnot\s+eligible\s+to\s+work\s+on\s+a\s+(?:visa|work\s+permit)\b",
    r"\bcannot\s+sponsor\b",
    r"\bfuture\s+(?:visa\s+)?sponsorship\s+(?:is\s+)?(?:not\s+available|unavailable)\b",
]

# Compiled for performance
_POSITIVE_RE = [re.compile(p, re.IGNORECASE) for p in SPONSORSHIP_POSITIVE_PATTERNS]
_NEGATIVE_RE = [re.compile(p, re.IGNORECASE) for p in SPONSORSHIP_NEGATIVE_PATTERNS]


def detect_sponsorship(text: str) -> Tuple[SponsorshipStatus, str]:
    """
    Analyze job text and return (SponsorshipStatus, explanation).
    Returns the most definitive signal found.
    """
    if not text:
        return SponsorshipStatus.unknown, "No text to analyze"

    positive_hits = []
    negative_hits = []

    for pattern in _POSITIVE_RE:
        match = pattern.search(text)
        if match:
            positive_hits.append(match.group(0).strip())

    for pattern in _NEGATIVE_RE:
        match = pattern.search(text)
        if match:
            negative_hits.append(match.group(0).strip())

    # Check for H1B transfer specifically
    h1b_transfer = re.search(r"\bh[\-\s]?1[\-\s]?b\s+transfer\b", text, re.IGNORECASE)

    if negative_hits and not positive_hits:
        return SponsorshipStatus.not_available, f"Found: {'; '.join(negative_hits[:2])}"

    if h1b_transfer:
        return SponsorshipStatus.transfer_ok, f"H1B transfer mentioned: {h1b_transfer.group(0)}"

    if positive_hits:
        return SponsorshipStatus.available, f"Found: {'; '.join(positive_hits[:2])}"

    # Both positive and negative — negative usually overrides in practice
    if negative_hits and positive_hits:
        return SponsorshipStatus.not_available, f"Conflicting signals; negative: {negative_hits[0]}"

    return SponsorshipStatus.unknown, "No sponsorship information found"


def sponsorship_score_for_user(
    status: SponsorshipStatus,
    requires_sponsorship: bool
) -> float:
    """
    Return a score factor (0.0 - 1.0) based on sponsorship alignment.
    If user doesn't require sponsorship, sponsorship status is neutral.
    """
    if not requires_sponsorship:
        return 0.75  # neutral-positive if not needed

    score_map = {
        SponsorshipStatus.available:     1.0,
        SponsorshipStatus.transfer_ok:   1.0,
        SponsorshipStatus.unknown:       0.5,
        SponsorshipStatus.not_available: 0.0,
    }
    return score_map.get(status, 0.5)
