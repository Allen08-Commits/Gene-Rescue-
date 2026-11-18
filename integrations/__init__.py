
"""External biological database integrations."""

from datetime import datetime, timezone
from typing import Any

import requests


class ExternalDatabaseError(Exception):
    """Raised when an external database cannot return usable data."""


def request_json(
    url: str,
    params: dict | None = None,
    headers: dict | None = None,
    timeout: int = 30,
) -> Any:
    """Perform a GET request and return JSON with consistent error handling."""
    request_headers = {
        "User-Agent": "GeneRescueAI/1.0 (bioinformatics research application)",
        "Accept": "application/json",
    }
    if headers:
        request_headers.update(headers)

    try:
        response = requests.get(
            url,
            params=params,
            headers=request_headers,
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise ExternalDatabaseError(
            f"External database request failed: {exc}"
        ) from exc
    except ValueError as exc:
        raise ExternalDatabaseError(
            "The database returned a response that was not valid JSON."
        ) from exc


def request_text(
    url: str,
    params: dict | None = None,
    headers: dict | None = None,
    timeout: int = 30,
) -> str:
    """Perform a GET request and return its text response."""
    request_headers = {
        "User-Agent": "GeneRescueAI/1.0 (bioinformatics research application)"
    }
    if headers:
        request_headers.update(headers)

    try:
        response = requests.get(
            url,
            params=params,
            headers=request_headers,
            timeout=timeout,
        )
        response.raise_for_status()
        return response.text
    except requests.RequestException as exc:
        raise ExternalDatabaseError(
            f"External database request failed: {exc}"
        ) from exc


def provenance(source: str, endpoint: str, query: dict | str) -> dict:
    """Create a record of where and when retrieved data came from."""
    return {
        "source": source,
        "endpoint": endpoint,
        "query": query,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
    }
