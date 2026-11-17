from __future__ import annotations

from radar_news_mcp.money import format_bps, funding_display_bps


def test_format_bps() -> None:
    assert format_bps(350) == "+3.50%"
    assert format_bps(-220) == "-2.20%"
    assert format_bps(0) == "0.00%"
    assert format_bps(None) == "n/a"


def test_funding_display_bps() -> None:
    # 500000 / 1e8 * 10000 = 50 bps display path via mul_div
    assert funding_display_bps(500000) == 50
