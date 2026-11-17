"""MCP stdio server — read-only radar digest / funding / listings tools."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from mcp.server.fastmcp import FastMCP

from radar_news_mcp.client import RadarClient, RadarClientError
from radar_news_mcp.digest import (
    DigestRefuse,
    collect_1h_movers,
    collect_extreme_funding,
    collect_listings_board,
    market_status,
)

mcp = FastMCP("dup-radar-news")


def _run(fn: Callable[[], dict[str, Any]]) -> str:
    try:
        data = fn()
        return json.dumps(data, ensure_ascii=False, default=str)
    except DigestRefuse as exc:
        return json.dumps(exc.as_dict(), ensure_ascii=False, default=str)
    except RadarClientError as exc:
        return json.dumps(exc.as_dict(), ensure_ascii=False, default=str)


@mcp.tool()
def radar_market_status() -> str:
    """Compact radar snapshot status (ok / age / sectors). Allowed when degraded."""

    def _inner() -> dict[str, Any]:
        return market_status(RadarClient().snapshot())

    return _run(_inner)


@mcp.tool()
def radar_digest_1h(top_n: int = 5) -> str:
    """1h gainers/losers from spot_alts + memes + listings. Refuses if ok=false."""

    def _inner() -> dict[str, Any]:
        return collect_1h_movers(RadarClient().snapshot(), top_n=top_n)

    return _run(_inner)


@mcp.tool()
def radar_funding_extremes(top_n: int = 8) -> str:
    """Extreme funding rows (display-only). Never enables futures auto."""

    def _inner() -> dict[str, Any]:
        return collect_extreme_funding(RadarClient().snapshot(), top_n=top_n)

    return _run(_inner)


@mcp.tool()
def radar_listings_board(top_n: int = 10) -> str:
    """Listings sector board from live snapshot. Refuses if ok=false."""

    def _inner() -> dict[str, Any]:
        return collect_listings_board(RadarClient().snapshot(), top_n=top_n)

    return _run(_inner)


@mcp.tool()
def radar_news_policy() -> str:
    """Hard policy surface for this MCP (no orders / no futures auto)."""
    return json.dumps(
        {
            "ok": True,
            "product": "dup-radar-news-mcp",
            "read_only": True,
            "futures_auto": False,
            "order_placement": False,
            "invent_prices": False,
            "source": "GET /api/snapshot from dup-market-radar",
            "note": "not financial advice; FUTURES_BLOCK",
        },
        ensure_ascii=False,
    )


def main() -> None:
    mcp.run(transport="stdio")
