"""Offline demo: digests from packaged fixtures (no live radar / no keys)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from radar_news_mcp.digest import (
    DigestRefuse,
    collect_1h_movers,
    collect_extreme_funding,
    collect_listings_board,
    market_status,
)


def _fixtures() -> Path:
    return Path(__file__).resolve().parents[2] / "tests" / "fixtures"


def main() -> int:
    root = _fixtures()
    ok_path = root / "snapshot_ok.json"
    deg_path = root / "snapshot_degraded.json"
    if not ok_path.is_file() or not deg_path.is_file():
        print(f"FAIL: fixtures missing under {root}", file=sys.stderr)
        return 2

    snap_ok = json.loads(ok_path.read_text(encoding="utf-8"))
    snap_deg = json.loads(deg_path.read_text(encoding="utf-8"))

    print("radar_news_mcp DEMO (fixtures — not live radar)")
    status = market_status(snap_ok)
    print(f" status ok={status.get('ok')} sectors={status.get('sector_counts')}")

    movers = collect_1h_movers(snap_ok, top_n=3)
    print(
        f" digest_1h gainers={[r['symbol'] for r in movers['gainers']]} "
        f"losers={[r['symbol'] for r in movers['losers']]}"
    )

    funding = collect_extreme_funding(snap_ok, top_n=3)
    print(
        f" funding_extremes n={len(funding['rows'])} futures_auto={funding['futures_auto']}"
    )

    listings = collect_listings_board(snap_ok, top_n=5)
    print(f" listings_board n={listings['n']}")

    refused = False
    try:
        collect_1h_movers(snap_deg)
    except DigestRefuse as exc:
        refused = True
        print(f" degraded digest → REFUSE ({exc.reason})")
    if not refused:
        print("FAIL: expected DigestRefuse on degraded snapshot", file=sys.stderr)
        return 1

    print("DEMO PASS — no KuCoin keys, no live radar required")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
