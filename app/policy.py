import json
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .config import LATE_RULES_JSON

@dataclass
class LateResult:
    is_late: bool
    late_minutes: int
    grace_applied: bool
    penalty_percent: int

def parse_canvas_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    if not dt_str:
        return None
    try:
        if dt_str.endswith("Z"):
            dt_str = dt_str[:-1] + "+00:00"
        return datetime.fromisoformat(dt_str)
    except Exception:
        return None

def compute_late(due_at: Optional[datetime], submitted_at: Optional[datetime]) -> LateResult:
    if not due_at or not submitted_at:
        return LateResult(False, 0, False, 0)

    delta = submitted_at - due_at
    late_minutes = int(delta.total_seconds() // 60)

    if late_minutes <= 0:
        return LateResult(False, 0, False, 0)

    rules = None
    if LATE_RULES_JSON:
        try:
            rules = json.loads(LATE_RULES_JSON)
        except Exception:
            rules = None

    # If no deterministic rules configured, report lateness but apply no penalty.
    if not rules:
        return LateResult(True, late_minutes, False, 0)

    grace = int(rules.get("grace_minutes", 0))
    if late_minutes <= grace:
        return LateResult(False, late_minutes, True, 0)

    late_hours = late_minutes / 60.0
    penalty = 0
    for tier in rules.get("tiers", []):
        max_h = float(tier.get("max_hours", 999999))
        if late_hours <= max_h:
            penalty = int(tier.get("penalty_percent", 0))
            break

    return LateResult(True, late_minutes, False, penalty)
