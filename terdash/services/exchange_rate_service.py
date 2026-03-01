"""Exchange rate service — free API with in-memory cache and fallback rates."""

import time

import httpx

# In-memory cache: {base_currency: (timestamp, {target: rate, ...})}
_cache: dict[str, tuple[float, dict[str, float]]] = {}
_CACHE_TTL = 3600  # 1 hour

# Hardcoded fallback rates (to JPY)
_FALLBACK_TO_JPY = {
    "USD": 150.0,
    "CNY": 20.7,
    "EUR": 163.0,
    "JPY": 1.0,
}


def get_rate(from_currency: str, to_currency: str) -> float:
    """Get exchange rate from one currency to another.

    Uses https://open.er-api.com (free, no key required).
    Falls back to hardcoded rates on failure.
    """
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    if from_currency == to_currency:
        return 1.0

    # Check cache
    now = time.time()
    if from_currency in _cache:
        ts, rates = _cache[from_currency]
        if now - ts < _CACHE_TTL and to_currency in rates:
            return rates[to_currency]

    # Fetch fresh rates
    try:
        resp = httpx.get(
            f"https://open.er-api.com/v6/latest/{from_currency}",
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("result") == "success":
            rates = data["rates"]
            _cache[from_currency] = (now, rates)
            if to_currency in rates:
                return rates[to_currency]
    except Exception:
        pass

    # Fallback: compute via JPY pivot
    return _fallback_rate(from_currency, to_currency)


def convert(amount: float, from_currency: str, to_currency: str) -> float:
    """Convert an amount from one currency to another."""
    return amount * get_rate(from_currency, to_currency)


def _fallback_rate(from_currency: str, to_currency: str) -> float:
    """Compute rate using hardcoded JPY pivot table."""
    from_to_jpy = _FALLBACK_TO_JPY.get(from_currency, 1.0)
    to_to_jpy = _FALLBACK_TO_JPY.get(to_currency, 1.0)
    return from_to_jpy / to_to_jpy
