"""Subscription data service — local JSON file storage."""

import json
from datetime import date, timedelta
from pathlib import Path

# Storage location: ~/.terdash/subscriptions.json
_DATA_DIR = Path.home() / ".terdash"
_DATA_FILE = _DATA_DIR / "subscriptions.json"


def _ensure_data_file():
    """Create the data directory and file if they don't exist."""
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not _DATA_FILE.exists():
        _DATA_FILE.write_text("[]", encoding="utf-8")


def _load_all() -> list[dict]:
    """Load all subscriptions from the JSON file."""
    _ensure_data_file()
    try:
        data = json.loads(_DATA_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _save_all(subs: list[dict]):
    """Save all subscriptions to the JSON file."""
    _ensure_data_file()
    _DATA_FILE.write_text(
        json.dumps(subs, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def get_subscriptions() -> list[dict]:
    """Fetch active subscriptions sorted by days_left.

    Returns list of dicts with keys:
        id, name, category, amount, currency, billing_cycle_days,
        next_billing_date, days_left.
    """
    today = date.today()
    result = []
    for s in _load_all():
        if not s.get("is_active", True):
            continue
        try:
            nbd = date.fromisoformat(s["next_billing_date"])
        except (KeyError, ValueError):
            continue
        days_left = (nbd - today).days
        result.append({
            "id": s.get("id", ""),
            "name": s["name"],
            "category": s.get("category", "其他"),
            "amount": float(s["amount"]),
            "currency": s.get("currency", "CNY"),
            "billing_cycle_days": s.get("billing_cycle_days", 30),
            "next_billing_date": s["next_billing_date"],
            "days_left": days_left,
        })
    result.sort(key=lambda x: x["days_left"])
    return result


def add_subscription(
    name: str,
    category: str,
    amount: float,
    currency: str,
    billing_cycle_days: int,
) -> dict:
    """Add a new subscription and return it.

    next_billing_date is auto-calculated as today + billing_cycle_days.
    """
    subs = _load_all()

    # Generate a simple incremental id
    max_id = max((s.get("id", 0) for s in subs), default=0)
    new_id = max_id + 1

    next_billing = (date.today() + timedelta(days=billing_cycle_days)).isoformat()

    entry = {
        "id": new_id,
        "name": name,
        "category": category,
        "amount": amount,
        "currency": currency,
        "billing_cycle_days": billing_cycle_days,
        "next_billing_date": next_billing,
        "is_active": True,
    }
    subs.append(entry)
    _save_all(subs)
    return entry


def delete_subscription(sub_id: int):
    """Delete a subscription by id."""
    subs = _load_all()
    subs = [s for s in subs if s.get("id") != sub_id]
    _save_all(subs)
