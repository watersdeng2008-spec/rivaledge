"""
Snapshot diff engine — compares two competitor snapshots and returns
meaningful, significance-ranked changes.
"""
from typing import Optional


# ── Significance mapping ───────────────────────────────────────────────────────

FIELD_SIGNIFICANCE = {
    "pricing": "high",
    "title": "high",
    "features": "medium",
    "ctas": "medium",
    "description": "low",
    "headings": "low",
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _list_diff(old_list: list, new_list: list, field: str) -> list[dict]:
    """Compute added/removed items between two lists."""
    old_set = set(str(x) for x in old_list)
    new_set = set(str(x) for x in new_list)

    added = new_set - old_set
    removed = old_set - new_set

    significance = FIELD_SIGNIFICANCE.get(field, "low")
    changes = []

    for item in sorted(added):
        changes.append({
            "field": field,
            "type": "added",
            "old_value": None,
            "new_value": item,
            "significance": significance,
        })

    for item in sorted(removed):
        changes.append({
            "field": field,
            "type": "removed",
            "old_value": item,
            "new_value": None,
            "significance": significance,
        })

    return changes


def _scalar_diff(old_val: str, new_val: str, field: str) -> Optional[dict]:
    """Compute a change for a scalar (string) field."""
    if old_val == new_val:
        return None
    significance = FIELD_SIGNIFICANCE.get(field, "low")
    return {
        "field": field,
        "type": "modified",
        "old_value": old_val or None,
        "new_value": new_val or None,
        "significance": significance,
    }


def _build_summary(changes: list[dict]) -> str:
    """Build a human-readable one-line summary of changes."""
    if not changes:
        return "No changes detected."

    high = [c for c in changes if c["significance"] == "high"]
    medium = [c for c in changes if c["significance"] == "medium"]
    low = [c for c in changes if c["significance"] == "low"]

    parts = []
    if high:
        fields = sorted(set(c["field"] for c in high))
        parts.append(f"High-impact changes: {', '.join(fields)}")
    if medium:
        fields = sorted(set(c["field"] for c in medium))
        parts.append(f"medium changes: {', '.join(fields)}")
    if low:
        fields = sorted(set(c["field"] for c in low))
        parts.append(f"minor changes: {', '.join(fields)}")

    total = len(changes)
    summary_prefix = f"{total} change{'s' if total != 1 else ''} detected — "
    return summary_prefix + "; ".join(parts)


# ── Public API ─────────────────────────────────────────────────────────────────

def diff_snapshots(old_snapshot: dict, new_snapshot: dict) -> dict:
    """
    Compare two snapshots and return meaningful changes.

    Args:
        old_snapshot: Previous snapshot content dict
        new_snapshot: New snapshot content dict

    Returns:
        {
            "has_changes": bool,
            "changes": [
                {
                    "field": str,
                    "type": "added" | "removed" | "modified",
                    "old_value": str | None,
                    "new_value": str | None,
                    "significance": "high" | "medium" | "low"
                }
            ],
            "summary": str
        }
    """
    changes: list[dict] = []

    # Scalar fields
    scalar_fields = ["title", "description"]
    for field in scalar_fields:
        old_val = str(old_snapshot.get(field, "") or "")
        new_val = str(new_snapshot.get(field, "") or "")
        change = _scalar_diff(old_val, new_val, field)
        if change:
            changes.append(change)

    # List fields
    list_fields = ["pricing", "features", "ctas", "headings"]
    for field in list_fields:
        old_list = old_snapshot.get(field, []) or []
        new_list = new_snapshot.get(field, []) or []
        field_changes = _list_diff(old_list, new_list, field)
        changes.extend(field_changes)

    # Sort by significance: high > medium > low
    sig_order = {"high": 0, "medium": 1, "low": 2}
    changes.sort(key=lambda c: sig_order.get(c["significance"], 3))

    return {
        "has_changes": len(changes) > 0,
        "changes": changes,
        "summary": _build_summary(changes),
    }
