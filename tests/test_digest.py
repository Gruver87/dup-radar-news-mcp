from __future__ import annotations

import json
from pathlib import Path

import pytest

from radar_news_mcp.digest import (
    DigestRefuse,
    collect_1h_movers,
    collect_extreme_funding,
    collect_listings_board,
    market_status,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_digest_1h_ok() -> None:
    data = collect_1h_movers(_load("snapshot_ok.json"), top_n=3)
    assert data["ok"] is True
    assert data["n_with_1h"] == 4
    assert data["gainers"][0]["symbol"] == "MEMEUSDT"
    assert data["gainers"][0]["change_bps_1h"] == 900
    assert data["losers"][0]["symbol"] == "BBBUSDT"
    assert "FUTURES_BLOCK" in data["note"]


def test_digest_refuses_degraded() -> None:
    with pytest.raises(DigestRefuse):
        collect_1h_movers(_load("snapshot_degraded.json"))


def test_funding_extremes() -> None:
    data = collect_extreme_funding(_load("snapshot_ok.json"), top_n=2)
    assert data["ok"] is True
    assert data["futures_auto"] is False
    assert data["rows"][0]["symbol"] == "ZZZUSDT"
    assert data["rows"][0]["funding_rate_i"] == -800000


def test_listings_board() -> None:
    data = collect_listings_board(_load("snapshot_ok.json"), top_n=5)
    assert data["n"] == 1
    assert data["rows"][0]["symbol"] == "NEWUSDT"


def test_market_status_allows_degraded() -> None:
    st = market_status(_load("snapshot_degraded.json"))
    assert st["ok"] is False
    assert st["futures_auto"] is False
