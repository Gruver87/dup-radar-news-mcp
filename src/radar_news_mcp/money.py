"""Integer money helpers — satoshi / 1e8 scale; no float theater."""

from __future__ import annotations

PRICE_SCALE = 100_000_000  # 1e8


def mul_div(a: int, b: int, den: int) -> int:
    if den == 0:
        raise ZeroDivisionError("mul_div denominator is 0")
    return (int(a) * int(b)) // int(den)


def funding_display_bps(funding_rate_i: int) -> int:
    """Map 1e8-fraction funding to display bps (100 bps = 1%)."""
    return int(mul_div(int(funding_rate_i), 10_000, PRICE_SCALE))


def format_bps(bps: int | None) -> str:
    if bps is None:
        return "n/a"
    v = int(bps)
    sign = "+" if v > 0 else ("-" if v < 0 else "")
    abs_v = abs(v)
    return f"{sign}{abs_v // 100}.{abs_v % 100:02d}%"
