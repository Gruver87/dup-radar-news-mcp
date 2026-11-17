# Architecture — dup-radar-news-mcp

**Org:** DUP Labs · **Surface:** read-only MCP digests over Market Radar snapshot

## Role

Companion to [`dup-agent-skills`](https://github.com/Gruver87/dup-agent-skills) `radar-ops` MCP.
That pack covers health/ready/trade **status**. This pack covers **market digest** tools:

| Tool | Source | Fail-closed |
|------|--------|-------------|
| `radar_market_status` | `/api/snapshot` | never invents; ok may be false |
| `radar_digest_1h` | sectors spot/memes/listings | refuses if `ok=false` |
| `radar_funding_extremes` | futures board | display-only; `futures_auto=false` |
| `radar_listings_board` | listings sector | refuses if `ok=false` |
| `radar_news_policy` | static | hard policy surface |

## Invariants

- Integer bps / `price_i` — no float PnL theater
- No place-order / no auto-enable / **FUTURES_BLOCK**
- Degraded snapshot → refuse digest/funding/listings claims
- Not a headline RSS scraper — “news” = market digest surface

## Related

- [`dup-market-radar`](https://github.com/Gruver87/dup-market-radar)
- [`dup-agent-skills`](https://github.com/Gruver87/dup-agent-skills)
- [`dup-skills-eval`](https://github.com/Gruver87/dup-skills-eval)
