#Requires -Version 5.1
<#
.SYNOPSIS
  Live smoke against RADAR_BASE_URL (default localhost:8787). Fail-closed.
#>
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$base = if ($env:RADAR_BASE_URL) { $env:RADAR_BASE_URL } else { "http://127.0.0.1:8787" }
Write-Host "smoke against $base"

python -c @"
from radar_news_mcp.client import RadarClient, RadarClientError
from radar_news_mcp.digest import (
    DigestRefuse,
    collect_1h_movers,
    collect_extreme_funding,
    collect_listings_board,
    market_status,
)

c = RadarClient()
try:
    snap = c.snapshot()
except RadarClientError as e:
    print('LIVE_SMOKE FAIL', e.as_dict())
    raise SystemExit(1)

st = market_status(snap)
print('status', st)
if not st.get('ok'):
    print('LIVE_SMOKE DEGRADED — digest tools should refuse')
    try:
        collect_1h_movers(snap)
        print('LIVE_SMOKE FAIL expected refuse')
        raise SystemExit(1)
    except DigestRefuse as e:
        print('refuse_ok', e.reason)
    print('LIVE_SMOKE PASS (degraded path)')
    raise SystemExit(0)

d = collect_1h_movers(snap, top_n=3)
f = collect_extreme_funding(snap, top_n=5)
l = collect_listings_board(snap, top_n=5)
print('digest_n', d.get('n_with_1h'), 'funding', len(f.get('rows') or []), 'listings', l.get('n'))
print('LIVE_SMOKE PASS')
"@

if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
exit 0
