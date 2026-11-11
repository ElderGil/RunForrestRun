"""Fail when the rolling plan stopped sliding (stale public data).

The daily routine regenerates data/weekly_plan.json with window_start = today.
If it stops running for any reason (Strava connection expired, Mac asleep,
session opened in plan mode, pipeline error), window_start falls behind.

Run by .github/workflows/freshness.yml once a day. A failed scheduled workflow
makes GitHub e-mail the repository owner, which turns any silent stop into an
alert the same day. Exit code 1 = stale.

    python etl/check_freshness.py [--max-lag-days N] [--today YYYY-MM-DD]
"""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

PLAN_PATH = Path(__file__).parent.parent / "data" / "weekly_plan.json"
BRT = timezone(timedelta(hours=-3))


def plan_lag_days(plan: dict, today: date) -> int | None:
    """Days between today and the plan's window_start (None if missing)."""
    start = plan.get("window_start")
    if not start:
        return None
    return (today - date.fromisoformat(start)).days


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-lag-days", type=int, default=1)
    parser.add_argument("--today", help="override today (YYYY-MM-DD), for tests")
    args = parser.parse_args(argv)

    today = date.fromisoformat(args.today) if args.today else datetime.now(BRT).date()
    plan = json.loads(PLAN_PATH.read_text())
    lag = plan_lag_days(plan, today)

    if lag is None:
        print("weekly_plan.json has no window_start")
        return 1
    if lag > args.max_lag_days:
        print(f"STALE: plan window starts {plan['window_start']}, {lag} day(s) behind {today}. "
              "The daily routine did not publish. See docs/automation-runbook.md.")
        return 1
    print(f"OK: plan window starts {plan['window_start']} ({lag} day(s) behind {today}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
