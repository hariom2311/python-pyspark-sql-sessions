import time
import requests
from config.settings import API_BASE_URL
from config.logger import get_logger

logger = get_logger("extractor")


def _fetch(token, endpoint, load_type="full", last_updated_at=None, max_pages=None):
    """Generic paginated fetch — same pattern for every API."""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Authorization": f"Token {token}"}

    all_records = []
    page = 1
    page_size = 100

    while True:
        params = {"page": page, "page_size": page_size}

        # incremental load — filter only records updated after last run
        if load_type == "incremental" and last_updated_at:
            params["updated_after"] = last_updated_at

        response = requests.get(url, headers=headers, params=params)

        # rate limit hit — wait and retry
        if response.status_code == 429:
            logger.warning(f"Rate limit hit on {endpoint}, waiting 10 seconds...")
            time.sleep(10)
            continue

        logger.info(f"Page {page} — status {response.status_code}")
        data = response.json()

        records     = data["data"]
        total_pages = data["pagination"]["total_pages"]

        all_records.extend(records)
        logger.info(f"Page {page}/{total_pages} — {len(records)} records fetched")

        if page >= total_pages:
            break

        if max_pages and page >= max_pages:
            logger.warning(f"Reached max_pages limit ({max_pages}), stopping early")
            break

        page += 1
        time.sleep(0.3)   # small pause between pages to avoid rate limit

    logger.info(f"Total fetched from {endpoint}: {len(all_records)}")
    return all_records


# ── Public fetch functions — one per API ────────────────────────────────────

def fetch_payments(token, load_type="full", last_updated_at=None, max_pages=None):
    logger.info("Fetching: payments")
    return _fetch(token, "/api/db/payments/", load_type, last_updated_at, max_pages)

def fetch_sessions(token, load_type="full", last_updated_at=None, max_pages=None):
    logger.info("Fetching: charging sessions")
    return _fetch(token, "/api/db/sessions/", load_type, last_updated_at, max_pages)

def fetch_customers(token, load_type="full", last_updated_at=None, max_pages=None):
    logger.info("Fetching: customers")
    return _fetch(token, "/api/db/customers/", load_type, last_updated_at, max_pages)

def fetch_vehicles(token, load_type="full", last_updated_at=None, max_pages=None):
    logger.info("Fetching: vehicles")
    return _fetch(token, "/api/db/vehicles/", load_type, last_updated_at, max_pages)

def fetch_stations(token, load_type="full", last_updated_at=None, max_pages=None):
    logger.info("Fetching: charging stations")
    return _fetch(token, "/api/db/stations/", load_type, last_updated_at, max_pages)

def fetch_partners(token, load_type="full", last_updated_at=None, max_pages=None):
    logger.info("Fetching: partners")
    return _fetch(token, "/api/db/partners/", load_type, last_updated_at, max_pages)

def fetch_energy_prices(token, load_type="full", last_updated_at=None, max_pages=None):
    logger.info("Fetching: energy prices")
    return _fetch(token, "/api/db/energy-prices/", load_type, last_updated_at, max_pages)
