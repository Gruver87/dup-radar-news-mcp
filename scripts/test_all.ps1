#Requires -Version 5.1
<#
.SYNOPSIS
  Unit + ruff gate for dup-radar-news-mcp (no network required).
#>
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Assert-NativeExit {
  param([Parameter(Mandatory)][string]$Label)
  if ($null -eq $LASTEXITCODE) { return }
  if ($LASTEXITCODE -ne 0) {
    throw "$Label failed with exit $LASTEXITCODE"
  }
}

Write-Host "== pip install -e .[dev] =="
python -m pip install -e ".[dev]" -q
Assert-NativeExit "pip"

Write-Host "== ruff =="
python -m ruff check src tests
Assert-NativeExit "ruff"

Write-Host "== pytest =="
python -m pytest -q
Assert-NativeExit "pytest"

Write-Host "test_all PASS"
exit 0
