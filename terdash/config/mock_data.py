"""Mock data for development without live API access."""

import random
from datetime import datetime, timedelta


def generate_mock_contributions(weeks: int = 52) -> list[list[int]]:
    """Generate mock GitHub contribution data.

    Returns a 7×weeks grid where each cell is a contribution count (0-15).
    Row 0 = Sunday, Row 6 = Saturday.
    """
    random.seed(42)
    grid = []
    for _day in range(7):
        row = []
        for _week in range(weeks):
            # Weight toward lower values with occasional spikes
            r = random.random()
            if r < 0.25:
                count = 0
            elif r < 0.55:
                count = random.randint(1, 3)
            elif r < 0.80:
                count = random.randint(4, 8)
            else:
                count = random.randint(9, 15)
            row.append(count)
        grid.append(row)
    return grid


def get_mock_streak() -> dict:
    """Return mock streak data."""
    return {
        "current_streak": 42,
        "yearly_total": 1247,
    }


def get_mock_code_time() -> list[dict]:
    """Return mock code time data for today."""
    return [
        {"language": "Python", "hours": 4.2, "color": "#3572A5"},
        {"language": "JavaScript", "hours": 2.8, "color": "#f1e05a"},
        {"language": "TypeScript", "hours": 1.5, "color": "#3178c6"},
        {"language": "Go", "hours": 0.9, "color": "#00ADD8"},
        {"language": "Rust", "hours": 0.4, "color": "#dea584"},
    ]


