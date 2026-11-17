#Requires -Version 5.1
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
python -m pip install -e ".[dev]" -q
python -m radar_news_mcp.demo
exit $LASTEXITCODE
