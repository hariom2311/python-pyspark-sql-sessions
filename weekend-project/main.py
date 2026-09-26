from api.auth import get_token
from database.connection import get_connection
from config.logger import get_logger
from etl.extractor import (
    fetch_payments,
    fetch_sessions,
    fetch_customers,
    fetch_vehicles,
    fetch_stations,
    fetch_partners,
    fetch_energy_prices,
)
from etl.transformer import (
    transform_payments,
    transform_sessions,
    transform_customers,
    transform_vehicles,
    transform_stations,
    transform_partners,
    transform_energy_prices,
)
from etl.loader import (
    create_tables,
    get_last_updated_at,
    insert_payments,
    insert_sessions,
    insert_customers,
    insert_vehicles,
    insert_stations,
    insert_partners,
    insert_energy_prices,
    save_pipeline_metadata,
)

logger = get_logger("main")

# ── Config ────────────────────────────────────────────────────────────────────
# set to "full" or "incremental"
LOAD_TYPE = "incremental"

# limit pages per API for testing — set to None for full load
MAX_PAGES = 5

# list of all pipelines to run: (pipeline_name, fetch_fn, transform_fn, insert_fn)
PIPELINES = [
    ("payments",      fetch_payments,      transform_payments,      insert_payments),
    ("sessions",      fetch_sessions,      transform_sessions,      insert_sessions),
    ("customers",     fetch_customers,     transform_customers,     insert_customers),
    ("vehicles",      fetch_vehicles,      transform_vehicles,      insert_vehicles),
    ("stations",      fetch_stations,      transform_stations,      insert_stations),
    ("partners",      fetch_partners,      transform_partners,      insert_partners),
    ("energy_prices", fetch_energy_prices, transform_energy_prices, insert_energy_prices),
]

# ── Setup ─────────────────────────────────────────────────────────────────────

connection = get_connection()
create_tables(connection)
token = get_token()

# ── Run each pipeline ─────────────────────────────────────────────────────────

for pipeline_name, fetch_fn, transform_fn, insert_fn in PIPELINES:
    logger.info(f"--- Pipeline: {pipeline_name.upper()} ---")
    try:
        load_type       = LOAD_TYPE
        last_updated_at = None

        if load_type == "incremental":
            last_updated_at = get_last_updated_at(connection, pipeline_name)
            logger.info(f"Last updated at: {last_updated_at}")

            if last_updated_at is None:
                logger.info("No previous run found — switching to full load")
                load_type = "full"

        raw_records   = fetch_fn(token, load_type=load_type,
                                 last_updated_at=last_updated_at, max_pages=MAX_PAGES)
        clean_records = transform_fn(raw_records)
        insert_fn(connection, clean_records)

        if clean_records:
            max_updated_at = max(r["updated_at"] for r in clean_records if r.get("updated_at"))
        else:
            max_updated_at = last_updated_at

        save_pipeline_metadata(connection, pipeline_name, load_type,
                               len(clean_records), max_updated_at)

    except Exception as e:
        logger.error(f"Pipeline '{pipeline_name}' failed: {e}")
        logger.info(f"Skipping '{pipeline_name}' — continuing with next pipeline")
        continue

# ── Done ──────────────────────────────────────────────────────────────────────

connection.close()
logger.info("All pipelines complete")
