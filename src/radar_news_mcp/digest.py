"""Build digests from radar snapshot — fail-closed when degraded."""

from __future__ import annotations

from typing import Any

from radar_news_mcp.money import format_bps, funding_display_bps

DIGEST_SECTORS = ("spot_alts", "memes", "listings")
NOTE = "not financial advice; read-only; no order placement; FUTURES_BLOCK"


class DigestRefuse(Exception):
    """Snapshot refused for digest claims."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason

    def as_dict(self) -> dict[str, Any]:
        return {"ok": False, "refused": True, "reason": self.reason, "note": NOTE}


def require_ok_snapshot(snap: dict[str, Any]) -> None:
    if snap.get("ok") is False:
        raise DigestRefuse("snapshot degraded (ok=false) — digest refused")
    if "ok" not in snap and not snap.get("sectors"):
        raise DigestRefuse("snapshot missing ok/sectors — digest refused")


def _metrics(row: dict[str, Any]) -> dict[str, Any]:
    m = row.get("metrics")
    return m if isinstance(m, dict) else {}


def _row_bps_1h(row: dict[str, Any]) -> int | None:
    v = _metrics(row).get("change_bps_1h")
    if v is None:
        v = row.get("change_bps_1h")
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _row_funding_i(row: dict[str, Any]) -> int | None:
    v = _metrics(row).get("funding_rate_i")
    if v is None:
        v = row.get("funding_rate_i")
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _cache_age_ms(snap: dict[str, Any]) -> int | None:
    cache = snap.get("cache") if isinstance(snap.get("cache"), dict) else {}
    for key in ("age_ms", "age_ms_est"):
        v = cache.get(key)
        if v is not None:
            try:
                return int(v)
            except (TypeError, ValueError):
                return None
    return None


def market_status(snap: dict[str, Any]) -> dict[str, Any]:
    """Compact status — allowed even when ok=false (honesty surface)."""
    auto = snap.get("auto_trade") if isinstance(snap.get("auto_trade"), dict) else {}
    sectors = snap.get("sectors") if isinstance(snap.get("sectors"), dict) else {}
    counts = {
        k: len(v) if isinstance(v, list) else 0
        for k, v in sectors.items()
        if k in ("spot_alts", "memes", "listings", "futures")
    }
    return {
        "ok": bool(snap.get("ok")),
        "product": snap.get("product") or "DUP Market Radar",
        "schema_version": snap.get("schema_version"),
        "generated_at_ms": snap.get("generated_at_ms") or snap.get("generated_at"),
        "universe_size": snap.get("universe_size"),
        "mtf_ensure_ok": snap.get("mtf_ensure_ok"),
        "cache_age_ms": _cache_age_ms(snap),
        "sector_counts": counts,
        "auto_enabled": auto.get("enabled"),
        "futures_auto": False,
        "note": NOTE,
    }


def collect_1h_movers(
    snap: dict[str, Any],
    *,
    top_n: int = 5,
    sectors: tuple[str, ...] = DIGEST_SECTORS,
) -> dict[str, Any]:
    require_ok_snapshot(snap)
    top_n = max(1, min(20, int(top_n)))
    seen: dict[str, dict[str, Any]] = {}
    for sector in sectors:
        rows = (snap.get("sectors") or {}).get(sector) or []
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            sym = str(row.get("symbol") or "").upper()
            bps = _row_bps_1h(row)
            if not sym or bps is None:
                continue
            prev = seen.get(sym)
            if prev is None or abs(bps) > abs(int(prev["change_bps_1h"])):
                seen[sym] = {
                    "symbol": sym,
                    "change_bps_1h": int(bps),
                    "change_display": format_bps(int(bps)),
                    "price_i": row.get("price_i"),
                    "sector": sector,
                }
    items = list(seen.values())
    gain = sorted(items, key=lambda r: int(r["change_bps_1h"]), reverse=True)[:top_n]
    lose = sorted(items, key=lambda r: int(r["change_bps_1h"]))[:top_n]
    return {
        "ok": True,
        "kind": "digest_1h",
        "n_with_1h": len(items),
        "top_n": top_n,
        "gainers": gain,
        "losers": lose,
        "cache_age_ms": _cache_age_ms(snap),
        "note": NOTE,
    }


def collect_extreme_funding(snap: dict[str, Any], *, top_n: int = 8) -> dict[str, Any]:
    """Funding extremes from futures board — display only; never enables futures auto."""
    require_ok_snapshot(snap)
    top_n = max(1, min(20, int(top_n)))
    rows = (snap.get("sectors") or {}).get("futures") or []
    if not isinstance(rows, list):
        rows = []
    if not rows:
        for key in ("futures_long", "futures_short"):
            part = (snap.get("sectors") or {}).get(key) or []
            if isinstance(part, list):
                rows.extend(part)
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        sym = str(row.get("symbol") or "").upper()
        fr = _row_funding_i(row)
        if not sym or fr is None or sym in seen:
            continue
        seen.add(sym)
        out.append(
            {
                "symbol": sym,
                "funding_rate_i": int(fr),
                "funding_display_bps": funding_display_bps(int(fr)),
                "funding_display": format_bps(funding_display_bps(int(fr))),
                "price_i": row.get("price_i"),
            }
        )
    out.sort(key=lambda r: abs(int(r["funding_rate_i"])), reverse=True)
    return {
        "ok": True,
        "kind": "funding_extremes",
        "top_n": top_n,
        "rows": out[:top_n],
        "futures_auto": False,
        "cache_age_ms": _cache_age_ms(snap),
        "note": NOTE + "; funding is display-only",
    }


def collect_listings_board(snap: dict[str, Any], *, top_n: int = 10) -> dict[str, Any]:
    require_ok_snapshot(snap)
    top_n = max(1, min(50, int(top_n)))
    rows = (snap.get("sectors") or {}).get("listings") or []
    if not isinstance(rows, list):
        rows = []
    board: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        sym = str(row.get("symbol") or "").upper()
        if not sym:
            continue
        bps = _row_bps_1h(row)
        board.append(
            {
                "symbol": sym,
                "change_bps_1h": bps,
                "change_display": format_bps(bps) if bps is not None else None,
                "price_i": row.get("price_i"),
                "setup": row.get("setup"),
                "score": row.get("score"),
            }
        )
        if len(board) >= top_n:
            break
    return {
        "ok": True,
        "kind": "listings_board",
        "top_n": top_n,
        "n": len(board),
        "rows": board,
        "cache_age_ms": _cache_age_ms(snap),
        "note": NOTE,
    }
