"""HTTP client for DUP Market Radar snapshot (read-only)."""

from __future__ import annotations

import os
from typing import Any

import httpx

DEFAULT_BASE = "http://127.0.0.1:8787"
TIMEOUT_S = 10.0


class RadarClientError(Exception):
    """Structured fail-closed error — never invent market data."""

    def __init__(self, message: str, *, status: int | None = None, body: Any = None) -> None:
        super().__init__(message)
        self.status = status
        self.body = body

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "ok": False,
            "error": str(self),
            "note": "not financial advice; no order placement",
        }
        if self.status is not None:
            out["status"] = self.status
        if self.body is not None:
            out["detail"] = self.body
        return out


class RadarClient:
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: float = TIMEOUT_S,
    ) -> None:
        self.base_url = (base_url or os.environ.get("RADAR_BASE_URL") or DEFAULT_BASE).rstrip(
            "/"
        )
        self.api_key = api_key if api_key is not None else os.environ.get("RADAR_API_KEY")
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        h: dict[str, str] = {"Accept": "application/json"}
        if self.api_key:
            h["X-Radar-Api-Key"] = self.api_key
        return h

    def get_json(self, path: str, *, auth: bool = False) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        headers = self._headers() if auth or self.api_key else {"Accept": "application/json"}
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(url, headers=headers)
        except httpx.HTTPError as exc:
            raise RadarClientError(f"radar unreachable: {exc}") from exc
        try:
            data = resp.json()
        except ValueError:
            data = {"raw": (resp.text or "")[:500]}
        if resp.status_code >= 400:
            raise RadarClientError(
                f"radar HTTP {resp.status_code} for {path}",
                status=resp.status_code,
                body=data,
            )
        if not isinstance(data, dict):
            raise RadarClientError(
                f"unexpected payload type for {path}",
                status=resp.status_code,
            )
        return data

    def health(self) -> dict[str, Any]:
        return self.get_json("/api/health")

    def snapshot(self) -> dict[str, Any]:
        return self.get_json("/api/snapshot", auth=True)
