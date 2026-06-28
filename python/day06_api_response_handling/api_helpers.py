"""
api_helpers.py
==============
Shared utilities for Day 6 — API Response Handling.

Import this in the notebook:
    from api_helpers import get_with_retry, make_429, make_500, make_200, fake_sleep

What lives here (infrastructure, not the lesson):
    - get_with_retry   : GET with 429 / 5xx retry + exponential backoff + jitter
    - make_429         : build a fake 429 response (for demo cells)
    - make_500         : build a fake 500 response (for demo cells)
    - make_200         : build a fake 200 response (for demo cells)
    - fake_sleep       : patched time.sleep that prints instead of waiting (for demo cells)

Students: read this file once to understand the plumbing,
          then ignore it and focus on the notebook logic.
"""

import requests
import time
import random
from unittest.mock import MagicMock


# ── Production helper ─────────────────────────────────────────────────────────

def get_with_retry(url, params=None, max_retries=4, base_delay=1.0):
    """
    GET request with exponential backoff retry.

    Retry on:
        429  → respect Retry-After header, then retry
        5xx  → exponential backoff + jitter, then retry
        Timeout / ConnectionError → exponential backoff, then retry

    Raise immediately on:
        4xx (except 429) → client error, not transient — our bug

    Raises RuntimeError when all retries are exhausted.
    """
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, params=params, timeout=10)

            if resp.status_code == 429:
                wait = float(resp.headers.get("Retry-After", base_delay * (2 ** attempt)))
                print(f"  [429] Rate limited — waiting {wait:.1f}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait)
                continue

            if resp.status_code >= 500:
                wait = base_delay * (2 ** attempt) + random.uniform(0, 0.5)
                print(f"  [{resp.status_code}] Server error — retrying in {wait:.2f}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait)
                continue

            resp.raise_for_status()   # 4xx → immediate failure
            return resp.json()

        except requests.exceptions.Timeout:
            wait = base_delay * (2 ** attempt)
            print(f"  [Timeout] No response — retrying in {wait:.1f}s (attempt {attempt + 1}/{max_retries})")
            time.sleep(wait)

        except requests.exceptions.ConnectionError:
            wait = base_delay * (2 ** attempt)
            print(f"  [ConnectionError] — retrying in {wait:.1f}s (attempt {attempt + 1}/{max_retries})")
            time.sleep(wait)

    raise RuntimeError(f"All {max_retries} retries exhausted for {url}")


# ── Demo helpers (mock builders) ──────────────────────────────────────────────

def make_429(retry_after=2):
    """Fake HTTP 429 response with a Retry-After header."""
    r = MagicMock()
    r.status_code = 429
    r.headers = {"Retry-After": str(retry_after)}
    return r


def make_500():
    """Fake HTTP 500 response — internal server error."""
    r = MagicMock()
    r.status_code = 500
    r.headers = {}
    return r


def make_200(body):
    """Fake HTTP 200 response with a JSON body dict."""
    r = MagicMock()
    r.status_code = 200
    r.json.return_value = body
    r.raise_for_status.return_value = None
    return r


def fake_sleep(secs):
    """Drop-in replacement for time.sleep used in demo cells — prints instead of waiting."""
    print(f"        ↳ [would sleep {secs:.2f}s in production — skipped in demo]")
