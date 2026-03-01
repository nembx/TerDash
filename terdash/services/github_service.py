"""GitHub contributions service via GraphQL API with mock fallback."""

import asyncio
import os

from terdash.config.mock_data import generate_mock_contributions, get_mock_streak
from terdash.config.settings import GITHUB_TOKEN, GITHUB_USERNAME

GRAPHQL_QUERY = """
query($username: String!) {
  user(login: $username) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
          }
        }
      }
    }
  }
}
"""


async def fetch_contributions(username: str | None = None) -> dict:
    """Fetch GitHub contribution data.

    Returns real data if GITHUB_TOKEN is set, otherwise returns mock data.
    """
    token = os.environ.get("GITHUB_TOKEN", GITHUB_TOKEN)
    user = username or os.environ.get("GITHUB_USERNAME", GITHUB_USERNAME)

    if token:
        try:
            return await _fetch_real(user, token)
        except Exception:
            pass

    # Fallback to mock data
    grid = generate_mock_contributions()
    streak = get_mock_streak()
    return {
        "grid": grid,
        "current_streak": streak["current_streak"],
        "yearly_total": streak["yearly_total"],
    }


async def _fetch_real(username: str, token: str) -> dict:
    """Fetch real contribution data from GitHub GraphQL API."""
    import httpx

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.github.com/graphql",
            json={"query": GRAPHQL_QUERY, "variables": {"username": username}},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

    calendar = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = calendar["weeks"]

    # Convert to 7×N grid (row=day_of_week, col=week)
    grid = [[] for _ in range(7)]
    for week in weeks:
        for i, day in enumerate(week["contributionDays"]):
            grid[i].append(day["contributionCount"])

    # Calculate streak
    all_days = []
    for week in weeks:
        for day in week["contributionDays"]:
            all_days.append(day["contributionCount"])

    streak = 0
    for count in reversed(all_days):
        if count > 0:
            streak += 1
        else:
            break

    return {
        "grid": grid,
        "current_streak": streak,
        "yearly_total": calendar["totalContributions"],
    }


def fetch_contributions_sync(username: str | None = None) -> dict:
    """Synchronous wrapper for fetch_contributions(). For use in QThread."""
    return asyncio.run(fetch_contributions(username))
