"""Code time tracking service (mock-based)."""

from terdash.config.mock_data import get_mock_code_time


def get_code_time() -> list[dict]:
    """Return today's code time data per language."""
    return get_mock_code_time()
