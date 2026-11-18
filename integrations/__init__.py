
"""Shared utilities for external biological database APIs."""

import os
import requests


class ExternalDatabaseError(RuntimeError):
    """Raised when an external database request fails."""


DEFAULT_TIMEOUT = 30

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "GeneRescueAI/1.0 (Bioinformatics Research Platform)",
    "Accept": "application/json",
})


def request_json(url, params=None, headers=None, timeout=DEFAULT_TIMEOUT):
    """Send an HTTP request and return parsed JSON."""
    try:
        response = SESSION.get(
            url,
            params=params,
            headers=headers,
            timeout=timeout,
        )
        response.raise_for_status()

        try:
            return response.json()
        except ValueError as exc:
            raise ExternalDatabaseError(
                "The external service returned invalid JSON."
            ) from exc

    except requests.RequestException as exc:
        raise ExternalDatabaseError(
            f"External database request failed: {exc}"
        ) from exc


def request_text(url, params=None, headers=None, timeout=DEFAULT_TIMEOUT):
    """Send an HTTP request and return response text."""
    try:
        response = SESSION.get(
            url,
            params=params,
            headers=headers,
            timeout=timeout,
        )
        response.raise_for_status()
        return response.text

    except requests.RequestException as exc:
        raise ExternalDatabaseError(
            f"External database request failed: {exc}"
        ) from exc


def ncbi_parameters():
    """Return optional NCBI credentials and application identity."""
    params = {
        "tool": "GeneRescueAI",
        "email": os.getenv("NCBI_EMAIL", ""),
    }

    api_key = os.getenv("NCBI_API_KEY", "")

    if api_key:
        params["api_key"] = api_key

    return {
        key: value
        for key, value in params.items()
        if value
    }


def provenance(source, endpoint, query=None):
    """Create a source provenance record."""
    return {
        "source": source,
        "endpoint": endpoint,
        "query": query,
    }
