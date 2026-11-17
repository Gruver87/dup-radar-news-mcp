# DUP Radar News MCP

[![ci](https://github.com/Gruver87/dup-radar-news-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/Gruver87/dup-radar-news-mcp/actions/workflows/ci.yml)

**Org:** [DUP Labs](https://github.com/Gruver87) · **Author:** Uladzimir Dabranski  
**Version:** `0.1.0` · **Read-only** MCP digests for [DUP Market Radar](https://github.com/Gruver87/dup-market-radar)

Market digest surface for agents: **1h movers**, **funding extremes** (display-only), **listings board**, **status**.  
Not a headline scraper. Not a trading bot. **Not financial advice.**

| Repo | Role |
|------|------|
| [`dup-market-radar`](https://github.com/Gruver87/dup-market-radar) | Live snapshot `/api/snapshot` |
| [`dup-agent-skills`](https://github.com/Gruver87/dup-agent-skills) | Ops MCP (`radar_health`, …) |
| [`dup-skills-eval`](https://github.com/Gruver87/dup-skills-eval) | Skills evaluation gate |

## Tools

| Tool | Behavior |
|------|----------|
| `radar_market_status` | ok / age / sector counts (even if degraded) |
| `radar_digest_1h` | gainers/losers · refuses if `ok=false` |
| `radar_funding_extremes` | \|funding\| board · `futures_auto=false` |
| `radar_listings_board` | listings sector rows |
| `radar_news_policy` | hard policy JSON |

## Install

```powershell
cd C:\Users\vovun\Desktop\dup-radar-news-mcp
python -m pip install -e ".[dev]"
.\scripts\test_all.ps1
```

Copy `mcp.json` into Cursor MCP config (set `RADAR_API_KEY` if your radar requires it).

```powershell
# optional live smoke (radar must be up)
.\scripts\smoke_live.ps1
```

## Honesty

- Ops-ready ≠ 48h soak  
- Funding rows ≠ futures auto  
- Degraded snapshot → refuse digest claims  

[`docs/DISCLAIMER.md`](docs/DISCLAIMER.md) · [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

## License

MIT — [`LICENSE`](LICENSE).
