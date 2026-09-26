# Weekend Project — Day 3 Session Guide

**What we build today:** Production hardening + Silver layer  
**Phases covered:** Phase 2 (Steps 10–12) + Phase 3 (Steps 13–15)

---

## Before You Start

Run the existing pipeline once to confirm bronze is working:
```
python main.py
```
Check PostgreSQL — all 7 bronze tables should have data.

---

## PART 1 — Production Hardening

---

### Step 10 — Replace `print()` with `logging`

**Why explain this:**  
`print()` has no timestamps, no levels, no file output. When a pipeline fails at 3am, you need a log file. The `logging` module gives structure.

---

#### 10A — Create the logger utility

**Action:** Create a new file `config/logger.py`

```python
# config/logger.py

import logging
import os

def get_logger(name):
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger   # already configured — don't add duplicate handlers

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s  %(levelname)-8s  [%(name)s]  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # handler 1 — print to console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # handler 2 — write to pipeline.log file
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    file_handler = logging.FileHandler(f"{log_dir}/pipeline.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
```

**Explain to students:**
- `getLogger(name)` — each module gets its own logger, shows the module name in output
- `StreamHandler` — logs to terminal
- `FileHandler` — also writes to `logs/pipeline.log`
- The `if logger.handlers` guard — prevents duplicate log lines when module is imported twice

**Output will look like:**
```
2024-08-09 22:05:01  INFO      [auth]       Token received
2024-08-09 22:05:02  INFO      [extractor]  Fetching: payments
2024-08-09 22:05:04  INFO      [extractor]  Page 1/5 — 100 records
2024-08-09 22:05:10  WARNING   [extractor]  Rate limit hit on /payments, waiting 10s
2024-08-09 22:05:21  ERROR     [loader]     Insert failed for payment_id PAY-999: ...
```

---

#### 10B — Update `api/auth.py`

**File:** `api/auth.py`  
**Change:** Replace every `print()` with `logger.info()`

**Before (current code):**
```python
import requests
from config.settings import API_BASE_URL, API_USERNAME, API_PASSWORD


def get_token():
    url = f"{API_BASE_URL}/api/auth/login/"
    payload = {
        "username": API_USERNAME,
        "password": API_PASSWORD
    }

    response = requests.post(url, json=payload)
    print("Login status:", response.status_code)

    data = response.json()
    token = data["token"]
    print("Token received:", token)
    return token
```

**After:**
```python
import requests
from config.settings import API_BASE_URL, API_USERNAME, API_PASSWORD
from config.logger import get_logger

logger = get_logger("auth")


def get_token():
    url = f"{API_BASE_URL}/api/auth/login/"
    payload = {
        "username": API_USERNAME,
        "password": API_PASSWORD
    }

    response = requests.post(url, json=payload)
    logger.info(f"Login status: {response.status_code}")

    data = response.json()
    token = data["token"]
    logger.info("Token received successfully")
    return token
```

**Lines added:** 2 (import + `logger = get_logger(...)`)  
**Lines changed:** 2 (`print` → `logger.info`)  
**Note:** Don't log the actual token value — that's a security risk.

---

#### 10C — Update `database/connection.py`

**File:** `database/connection.py`  
**Change:** Replace `print()` with logger

**Before:**
```python
import psycopg2
from config.settings import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


def get_connection():
    connection = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    print("DB connection successful")
    return connection
```

**After:**
```python
import psycopg2
from config.settings import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
from config.logger import get_logger

logger = get_logger("database")


def get_connection():
    connection = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    logger.info(f"DB connection successful — {DB_NAME}@{DB_HOST}:{DB_PORT}")
    return connection
```

---

#### 10D — Update `etl/extractor.py`

**File:** `etl/extractor.py`  
**Change:** Replace all `print()` calls — add `logger.warning` for rate limit, `logger.error` for bad status

**Add at top of file (after existing imports):**
```python
from config.logger import get_logger
logger = get_logger("extractor")
```

**Replace every `print(...)` inside `_fetch()` and the public fetch functions:**

| Old `print()` | New `logger` call |
|---|---|
| `print(f"Rate limit hit on {endpoint}...")` | `logger.warning(f"Rate limit hit on {endpoint}, waiting 10s...")` |
| `print(f"  Page {page} status: ...")` | `logger.info(f"Page {page} — status {response.status_code}")` |
| `print(f"  Page {page}/{total_pages}...")` | `logger.info(f"Page {page}/{total_pages} — {len(records)} records")` |
| `print(f"  Reached max_pages limit...")` | `logger.warning(f"Reached max_pages limit ({max_pages}), stopping early")` |
| `print(f"  Total fetched: ...")` | `logger.info(f"Total fetched: {len(all_records)}")` |
| `print("Fetching: payments")` | `logger.info("Fetching: payments")` |
| *(same for all 7 fetch functions)* | |

**Full updated `_fetch()` function:**
```python
def _fetch(token, endpoint, load_type="full", last_updated_at=None, max_pages=None):
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Authorization": f"Token {token}"}

    all_records = []
    page = 1
    page_size = 100

    while True:
        params = {"page": page, "page_size": page_size}

        if load_type == "incremental" and last_updated_at:
            params["updated_after"] = last_updated_at

        response = requests.get(url, headers=headers, params=params)

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
        time.sleep(0.3)

    logger.info(f"Total fetched from {endpoint}: {len(all_records)}")
    return all_records
```

---

#### 10E — Update `etl/transformer.py`

**File:** `etl/transformer.py`  
**Add at top:**
```python
from config.logger import get_logger
logger = get_logger("transformer")
```

**Replace every `print(f"  Transformed {len(clean_records)} ...")` with:**
```python
logger.info(f"Transformed {len(clean_records)} payment records")
# (same pattern for each of the 7 transform functions — just change the entity name)
```

---

#### 10F — Update `etl/loader.py`

**File:** `etl/loader.py`  
**Add at top:**
```python
from config.logger import get_logger
logger = get_logger("loader")
```

**Replace all `print()` calls:**

| Old | New |
|---|---|
| `print("All bronze tables ready")` | `logger.info("All bronze tables created/verified")` |
| `print(f"  Metadata saved for {pipeline_name}")` | `logger.info(f"Metadata saved for {pipeline_name}")` |
| `print(f"  Inserted {len(records)} records into bronze.payments")` | `logger.info(f"Inserted {len(records)} records into bronze.payments")` |
| *(same for all 7 insert functions)* | |

---

#### 10G — Update `main.py`

**File:** `main.py`  
**Add at top:**
```python
from config.logger import get_logger
logger = get_logger("main")
```

**Replace all `print()` calls:**

| Old | New |
|---|---|
| `print(f"\n{'='*50}")` | *(remove)* |
| `print(f"Pipeline: {pipeline_name.upper()}")` | `logger.info(f"--- Pipeline: {pipeline_name.upper()} ---")` |
| `print(f"Last updated at: {last_updated_at}")` | `logger.info(f"Last updated at: {last_updated_at}")` |
| `print("No previous run found, switching to full load")` | `logger.info("No previous run found — switching to full load")` |
| `print("All pipelines complete")` | `logger.info("All pipelines complete")` |

---

### Step 11 — Error Handling + Dead Letter Table

**Why explain this:**  
One corrupt record from the API currently crashes the whole pipeline. We want the pipeline to continue and save bad records for investigation.

---

#### 11A — Add the dead letter table to `etl/loader.py`

**File:** `etl/loader.py`  
**Where:** Inside `create_tables()`, after the `pipeline_metadata` table creation

**Add this block:**
```python
    # dead letter table — stores records that failed to insert
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bronze.failed_records (
            id            SERIAL PRIMARY KEY,
            pipeline_name TEXT,
            raw_record    TEXT,
            error_message TEXT,
            failed_at     TIMESTAMPTZ DEFAULT NOW()
        );
    """)
```

**Then add this new function** at the bottom of `loader.py`:
```python
def save_failed_record(connection, pipeline_name, record, error_message):
    import json
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO bronze.failed_records (pipeline_name, raw_record, error_message)
        VALUES (%s, %s, %s);
    """, (pipeline_name, json.dumps(record, default=str), error_message))
    connection.commit()
    logger.warning(f"Saved failed record for {pipeline_name}: {error_message}")
```

---

#### 11B — Wrap inserts in try/except

**File:** `etl/loader.py`  
**Where:** Inside each insert function — wrap the `cursor.executemany()` call

**Before (current `insert_payments`):**
```python
def insert_payments(connection, records):
    cursor = connection.cursor()
    query = """..."""
    cursor.executemany(query, records)
    connection.commit()
    print(f"  Inserted {len(records)} records into bronze.payments")
```

**After — row-by-row with error capture:**
```python
def insert_payments(connection, records):
    cursor = connection.cursor()
    query = """
        INSERT INTO bronze.payments (
            id, payment_id, session_id, customer_id, gateway,
            amount_aud, gst, payment_mode, status,
            processed_at, created_at, updated_at, ingested_at
        ) VALUES (
            %(id)s, %(payment_id)s, %(session_id)s, %(customer_id)s, %(gateway)s,
            %(amount_aud)s, %(gst)s, %(payment_mode)s, %(status)s,
            %(processed_at)s, %(created_at)s, %(updated_at)s, %(ingested_at)s
        )
        ON CONFLICT (id) DO UPDATE SET
            status       = EXCLUDED.status,
            amount_aud   = EXCLUDED.amount_aud,
            updated_at   = EXCLUDED.updated_at,
            ingested_at  = EXCLUDED.ingested_at;
    """

    success = 0
    failed  = 0

    for record in records:
        try:
            cursor.execute(query, record)
            connection.commit()
            success += 1
        except Exception as e:
            connection.rollback()
            failed += 1
            logger.error(f"Insert failed for payment_id {record.get('payment_id')}: {e}")
            save_failed_record(connection, "payments", record, str(e))

    logger.info(f"bronze.payments — inserted: {success}, failed: {failed}")
```

**Explain to students:**
- `executemany` → `for record + cursor.execute` — one record at a time so one bad record doesn't stop the rest
- `connection.rollback()` — cancel the failed record's transaction before continuing
- `connection.commit()` inside the loop — each record committed independently
- Apply the same pattern to all 7 insert functions

---

#### 11C — Wrap `main.py` pipeline loop in try/except

**File:** `main.py`  
**Where:** Inside the `for pipeline_name, ...` loop — wrap the entire pipeline body

**Before:**
```python
for pipeline_name, fetch_fn, transform_fn, insert_fn in PIPELINES:
    # Step 4: decide load type
    ...
    raw_records = fetch_fn(...)
    clean_records = transform_fn(raw_records)
    insert_fn(connection, clean_records)
    save_pipeline_metadata(...)
```

**After:**
```python
for pipeline_name, fetch_fn, transform_fn, insert_fn in PIPELINES:
    logger.info(f"--- Pipeline: {pipeline_name.upper()} ---")
    try:
        load_type = LOAD_TYPE
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
        logger.error(f"Pipeline {pipeline_name} failed: {e}")
        logger.info(f"Skipping {pipeline_name} — continuing with next pipeline")
        continue
```

**Explain:** `continue` means even if payments pipeline crashes, sessions pipeline still runs.

---

### Step 12 — Database Indexes

**Why explain this:**  
Without indexes, every query on `updated_at` or `status` scans the full table.
With 1 million rows, that takes seconds instead of milliseconds.

**File:** `etl/loader.py`  
**Where:** At the end of `create_tables()`, after all `CREATE TABLE` statements, before `connection.commit()`

**Add this block:**
```python
    # ── Indexes for query performance ────────────────────────────────────
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_updated_at  ON bronze.payments(updated_at);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_status      ON bronze.payments(status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_customer_id ON bronze.payments(customer_id);")

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_customer_id ON bronze.sessions(customer_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_station_id  ON bronze.sessions(station_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_started_at  ON bronze.sessions(started_at);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_updated_at  ON bronze.sessions(updated_at);")

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_customers_updated_at ON bronze.customers(updated_at);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_stations_state_code  ON bronze.stations(state_code);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_stations_updated_at  ON bronze.stations(updated_at);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_vehicles_vehicle_id  ON bronze.vehicles(vehicle_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_vehicles_is_current  ON bronze.vehicles(is_current);")

    logger.info("Indexes created/verified")
```

**Explain to students:**
- `CREATE INDEX IF NOT EXISTS` — safe to run every time, won't fail if index already exists
- `updated_at` indexes — used by incremental load cursor query
- `customer_id`, `station_id` — used when joining tables in Silver/Gold queries
- `is_current` on vehicles — used in SCD2 queries to filter active rows

---

**Test after Steps 10–12:**
```
python main.py
```
You should see:
- Structured log output in terminal with timestamps
- `logs/pipeline.log` file created
- No crash if a single bad record appears
- `bronze.failed_records` table exists in DB (empty is fine)

---

## PART 2 — Silver Layer

---

### Step 13 — Silver Schema & Tables

**Why explain this:**  
Bronze = raw API dump. It has nulls, inconsistent casing, test data.  
Silver = clean, validated, ready to query. This is what analysts and dashboards read.

---

#### 13A — Create `etl/silver_loader.py`

**Action:** Create a new file `etl/silver_loader.py`

```python
# etl/silver_loader.py

from config.logger import get_logger

logger = get_logger("silver_loader")


def create_silver_tables(connection):
    cursor = connection.cursor()

    cursor.execute("CREATE SCHEMA IF NOT EXISTS silver;")

    # silver.payments — cleaned, validated payment records
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS silver.payments (
            payment_id    VARCHAR(100) PRIMARY KEY,
            session_id    VARCHAR(100),
            customer_id   VARCHAR(100),
            gateway       VARCHAR(50),
            amount_aud    NUMERIC(12, 2)  NOT NULL,
            gst           NUMERIC(12, 2),
            payment_mode  VARCHAR(50),
            status        VARCHAR(50)     NOT NULL,
            processed_at  TIMESTAMPTZ,
            created_at    TIMESTAMPTZ,
            updated_at    TIMESTAMPTZ,
            processed_at_silver TIMESTAMPTZ DEFAULT NOW()
        );
    """)

    # silver.sessions — cleaned charging session records
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS silver.sessions (
            session_id     VARCHAR(100) PRIMARY KEY,
            vehicle_id     VARCHAR(100),
            station_id     VARCHAR(100),
            customer_id    VARCHAR(100),
            started_at     TIMESTAMPTZ,
            ended_at       TIMESTAMPTZ,
            duration_min   INT,
            energy_kwh     NUMERIC(10, 3),
            cost_aud       NUMERIC(12, 2),
            peak_power_kw  NUMERIC(10, 2),
            connector_type VARCHAR(50),
            session_status VARCHAR(50),
            payment_id     VARCHAR(100),
            updated_at     TIMESTAMPTZ,
            processed_at_silver TIMESTAMPTZ DEFAULT NOW()
        );
    """)

    # silver.customers — deduplicated, validated customer records
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS silver.customers (
            customer_id   VARCHAR(100) PRIMARY KEY,
            full_name     VARCHAR(200),
            email         VARCHAR(200),
            phone         VARCHAR(50),
            loyalty_tier  VARCHAR(50),
            signup_date   DATE,
            updated_at    TIMESTAMPTZ,
            processed_at_silver TIMESTAMPTZ DEFAULT NOW()
        );
    """)

    # silver.vehicles_history — SCD2 full history of vehicle changes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS silver.vehicles_history (
            id                   SERIAL PRIMARY KEY,
            vehicle_id           VARCHAR(100)  NOT NULL,
            make                 VARCHAR(100),
            model                VARCHAR(100),
            year                 INT,
            vehicle_type         VARCHAR(20),
            battery_capacity_kwh NUMERIC(8, 2),
            range_km             INT,
            registration_state   VARCHAR(10),
            partner_id           VARCHAR(100),
            effective_from       DATE          NOT NULL,
            effective_to         DATE          NOT NULL DEFAULT '9999-12-31',
            is_current           BOOLEAN       NOT NULL DEFAULT TRUE,
            processed_at_silver  TIMESTAMPTZ   DEFAULT NOW()
        );
    """)

    connection.commit()
    logger.info("All silver tables created/verified")
```

---

### Step 14 — Silver Transformation (validate, clean, deduplicate)

**File:** Create `etl/silver_transformer.py`

```python
# etl/silver_transformer.py

from config.logger import get_logger

logger = get_logger("silver_transformer")


# ── Payments ──────────────────────────────────────────────────────────────────

def silver_transform_payments(bronze_records):
    """
    Rules applied:
    - Drop records missing payment_id or amount_aud
    - Drop test/dummy payments (payment_id starts with 'TEST')
    - Normalise status to lowercase and strip whitespace
    - Round amount_aud to 2 decimal places
    """
    clean   = []
    skipped = 0

    for r in bronze_records:
        # Rule 1 — required fields must be present
        if not r.get("payment_id") or not r.get("amount_aud"):
            skipped += 1
            continue

        # Rule 2 — exclude test records
        if str(r["payment_id"]).startswith("TEST"):
            skipped += 1
            continue

        clean.append({
            "payment_id"  : r["payment_id"],
            "session_id"  : r.get("session_id"),
            "customer_id" : r.get("customer_id"),
            "gateway"     : r.get("gateway"),
            "amount_aud"  : round(float(r["amount_aud"]), 2),
            "gst"         : round(float(r["gst"]), 2) if r.get("gst") else None,
            "payment_mode": r.get("payment_mode"),
            "status"      : r["status"].strip().lower(),   # normalise
            "processed_at": r.get("processed_at"),
            "created_at"  : r.get("created_at"),
            "updated_at"  : r.get("updated_at"),
        })

    logger.info(f"silver.payments — kept: {len(clean)}, skipped: {skipped}")
    return clean


# ── Sessions ──────────────────────────────────────────────────────────────────

def silver_transform_sessions(bronze_records):
    """
    Rules applied:
    - Drop records missing session_id or customer_id
    - Drop sessions with negative or zero energy_kwh
    - Normalise session_status to lowercase
    """
    clean   = []
    skipped = 0

    for r in bronze_records:
        if not r.get("session_id") or not r.get("customer_id"):
            skipped += 1
            continue

        energy = float(r["energy_kwh"]) if r.get("energy_kwh") else None
        if energy is not None and energy <= 0:
            skipped += 1
            continue

        clean.append({
            "session_id"    : r["session_id"],
            "vehicle_id"    : r.get("vehicle_id"),
            "station_id"    : r.get("station_id"),
            "customer_id"   : r["customer_id"],
            "started_at"    : r.get("started_at"),
            "ended_at"      : r.get("ended_at"),
            "duration_min"  : r.get("duration_min"),
            "energy_kwh"    : energy,
            "cost_aud"      : round(float(r["cost_aud"]), 2) if r.get("cost_aud") else None,
            "peak_power_kw" : float(r["peak_power_kw"]) if r.get("peak_power_kw") else None,
            "connector_type": r.get("connector_type"),
            "session_status": r["session_status"].strip().lower() if r.get("session_status") else None,
            "payment_id"    : r.get("payment_id"),
            "updated_at"    : r.get("updated_at"),
        })

    logger.info(f"silver.sessions — kept: {len(clean)}, skipped: {skipped}")
    return clean


# ── Customers ─────────────────────────────────────────────────────────────────

def silver_transform_customers(bronze_records):
    """
    Rules applied:
    - Drop records missing customer_id or email
    - Drop records where email contains 'test' or 'dummy'
    - Normalise loyalty_tier to uppercase
    """
    clean   = []
    skipped = 0

    for r in bronze_records:
        if not r.get("customer_id") or not r.get("email"):
            skipped += 1
            continue

        email = r["email"].strip().lower()
        if "test" in email or "dummy" in email:
            skipped += 1
            continue

        clean.append({
            "customer_id" : r["customer_id"],
            "full_name"   : r.get("full_name"),
            "email"       : email,
            "phone"       : r.get("phone"),
            "loyalty_tier": r["loyalty_tier"].strip().upper() if r.get("loyalty_tier") else None,
            "signup_date" : r.get("signup_date"),
            "updated_at"  : r.get("updated_at"),
        })

    logger.info(f"silver.customers — kept: {len(clean)}, skipped: {skipped}")
    return clean
```

---

### Step 15 — Insert into Silver tables

**File:** `etl/silver_loader.py`  
**Where:** Add after `create_silver_tables()` — new insert functions

```python
def insert_silver_payments(connection, records):
    cursor = connection.cursor()
    query = """
        INSERT INTO silver.payments (
            payment_id, session_id, customer_id, gateway,
            amount_aud, gst, payment_mode, status,
            processed_at, created_at, updated_at
        ) VALUES (
            %(payment_id)s, %(session_id)s, %(customer_id)s, %(gateway)s,
            %(amount_aud)s, %(gst)s, %(payment_mode)s, %(status)s,
            %(processed_at)s, %(created_at)s, %(updated_at)s
        )
        ON CONFLICT (payment_id) DO UPDATE SET
            status      = EXCLUDED.status,
            amount_aud  = EXCLUDED.amount_aud,
            updated_at  = EXCLUDED.updated_at,
            processed_at_silver = NOW();
    """
    success = 0
    failed  = 0
    for record in records:
        try:
            cursor.execute(query, record)
            connection.commit()
            success += 1
        except Exception as e:
            connection.rollback()
            failed += 1
            logger.error(f"Silver insert failed for payment_id {record.get('payment_id')}: {e}")

    logger.info(f"silver.payments — inserted: {success}, failed: {failed}")


def insert_silver_sessions(connection, records):
    cursor = connection.cursor()
    query = """
        INSERT INTO silver.sessions (
            session_id, vehicle_id, station_id, customer_id,
            started_at, ended_at, duration_min, energy_kwh, cost_aud,
            peak_power_kw, connector_type, session_status, payment_id, updated_at
        ) VALUES (
            %(session_id)s, %(vehicle_id)s, %(station_id)s, %(customer_id)s,
            %(started_at)s, %(ended_at)s, %(duration_min)s, %(energy_kwh)s, %(cost_aud)s,
            %(peak_power_kw)s, %(connector_type)s, %(session_status)s, %(payment_id)s, %(updated_at)s
        )
        ON CONFLICT (session_id) DO UPDATE SET
            session_status      = EXCLUDED.session_status,
            energy_kwh          = EXCLUDED.energy_kwh,
            cost_aud            = EXCLUDED.cost_aud,
            updated_at          = EXCLUDED.updated_at,
            processed_at_silver = NOW();
    """
    success = 0
    failed  = 0
    for record in records:
        try:
            cursor.execute(query, record)
            connection.commit()
            success += 1
        except Exception as e:
            connection.rollback()
            failed += 1
            logger.error(f"Silver insert failed for session_id {record.get('session_id')}: {e}")

    logger.info(f"silver.sessions — inserted: {success}, failed: {failed}")


def insert_silver_customers(connection, records):
    cursor = connection.cursor()
    query = """
        INSERT INTO silver.customers (
            customer_id, full_name, email, phone,
            loyalty_tier, signup_date, updated_at
        ) VALUES (
            %(customer_id)s, %(full_name)s, %(email)s, %(phone)s,
            %(loyalty_tier)s, %(signup_date)s, %(updated_at)s
        )
        ON CONFLICT (customer_id) DO UPDATE SET
            loyalty_tier        = EXCLUDED.loyalty_tier,
            email               = EXCLUDED.email,
            updated_at          = EXCLUDED.updated_at,
            processed_at_silver = NOW();
    """
    success = 0
    failed  = 0
    for record in records:
        try:
            cursor.execute(query, record)
            connection.commit()
            success += 1
        except Exception as e:
            connection.rollback()
            failed += 1
            logger.error(f"Silver insert failed for customer_id {record.get('customer_id')}: {e}")

    logger.info(f"silver.customers — inserted: {success}, failed: {failed}")
```

---

### Step 16 — Wire Silver into `main.py`

**File:** `main.py`  
**Where:** After the existing bronze pipeline loop — add a silver section at the bottom

**Add these imports at the top of `main.py`:**
```python
from etl.silver_loader import (
    create_silver_tables,
    insert_silver_payments,
    insert_silver_sessions,
    insert_silver_customers,
)
from etl.silver_transformer import (
    silver_transform_payments,
    silver_transform_sessions,
    silver_transform_customers,
)
```

**Add at the bottom of `main.py`**, after the bronze loop:
```python
# ── Silver Layer ──────────────────────────────────────────────────────────────

logger.info("Starting Silver layer processing")

# Create silver tables
create_silver_tables(connection)

# Read from bronze, transform, load into silver
SILVER_PIPELINES = [
    ("payments",  "bronze.payments",  silver_transform_payments,  insert_silver_payments),
    ("sessions",  "bronze.sessions",  silver_transform_sessions,  insert_silver_sessions),
    ("customers", "bronze.customers", silver_transform_customers, insert_silver_customers),
]

for name, bronze_table, transform_fn, insert_fn in SILVER_PIPELINES:
    logger.info(f"--- Silver Pipeline: {name.upper()} ---")
    try:
        cursor = connection.cursor()
        cursor.execute(f"SELECT row_to_json(t) FROM {bronze_table} t;")
        bronze_rows = [dict(row[0]) for row in cursor.fetchall()]
        logger.info(f"Read {len(bronze_rows)} rows from {bronze_table}")

        silver_records = transform_fn(bronze_rows)
        insert_fn(connection, silver_records)

    except Exception as e:
        logger.error(f"Silver pipeline {name} failed: {e}")
        continue

logger.info("Silver layer complete")
```

**Explain to students:**
- `row_to_json(t)` — PostgreSQL built-in that converts a row to JSON dict — easiest way to read bronze into Python without re-fetching from API
- Silver reads from bronze, not from the API — bronze is the single source of truth for all downstream layers

---

## Final File Summary — What Changed Today

| File | Action | What was done |
|---|---|---|
| `config/logger.py` | **NEW** | Centralised logger with console + file handlers |
| `logs/` | **NEW folder** | Created automatically by logger |
| `etl/silver_loader.py` | **NEW** | Silver schema creation + 3 insert functions |
| `etl/silver_transformer.py` | **NEW** | Validation + cleaning logic for payments, sessions, customers |
| `api/auth.py` | **EDITED** | `print()` → `logger.info()` |
| `database/connection.py` | **EDITED** | `print()` → `logger.info()` |
| `etl/extractor.py` | **EDITED** | `print()` → logger with warning for rate limit |
| `etl/transformer.py` | **EDITED** | `print()` → `logger.info()` |
| `etl/loader.py` | **EDITED** | `print()` → logger, dead letter table, indexes, row-by-row inserts with try/except |
| `main.py` | **EDITED** | Logger, pipeline try/except, silver section added at bottom |

---

## Run Order for the Session

```
1. python main.py          ← should run all bronze pipelines + silver layer
2. check logs/pipeline.log ← should have timestamped structured logs
3. in psql or DBeaver:
   SELECT * FROM bronze.failed_records;        -- should be empty
   SELECT COUNT(*) FROM silver.payments;       -- should have data
   SELECT COUNT(*) FROM silver.sessions;       -- should have data
   SELECT COUNT(*) FROM silver.customers;      -- should have data
   SELECT * FROM silver.payments LIMIT 5;      -- status should be lowercase
```
