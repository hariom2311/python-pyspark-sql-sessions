# VoltGrid EV Charging — ETL Pipeline Project

---

## Project Goal

Build a production-style data pipeline that:
1. Pulls live EV charging data from the VoltGrid REST API
2. Stores raw data in a **Bronze** layer (PostgreSQL)
3. Cleans and validates it into a **Silver** layer
4. Aggregates it into a **Gold** layer for analytics

---

## Architecture Overview

```
VoltGrid REST API
        |
   [Auth — Bearer Token]
        |
   Determine Load Type
   (Full Load OR Incremental based on last run)
        |
   Fetch Data with Pagination
   (handle 429 rate limit → wait → retry)
        |
   Transform (type cast, null handling, timestamps)
        |
   ┌─────────────────────────────────┐
   │         BRONZE LAYER            │  ← raw API data, minimal changes
   │  bronze.payments                │
   │  bronze.sessions                │
   │  bronze.customers               │
   │  bronze.vehicles                │
   │  bronze.stations                │
   │  bronze.partners                │
   │  bronze.energy_prices           │
   │  bronze.pipeline_metadata       │
   └─────────────────────────────────┘
        |
   [NEXT: Silver Layer]
        |
   ┌─────────────────────────────────┐
   │         SILVER LAYER            │  ← cleaned, validated, deduplicated
   │  silver.payments                │
   │  silver.sessions                │
   │  silver.customers               │
   │  silver.vehicles_history (SCD2) │
   └─────────────────────────────────┘
        |
   [NEXT: Gold Layer]
        |
   ┌─────────────────────────────────┐
   │          GOLD LAYER             │  ← aggregated, analytics-ready
   │  gold.daily_revenue             │
   │  gold.station_utilization       │
   │  gold.customer_summary          │
   └─────────────────────────────────┘
```

---

## Incremental Load Logic

```
Pipeline starts
      |
      ▼
Is bronze.payments empty?
      |
   YES → Full Load (fetch all records from API)
      |
   NO  → Incremental Load
         Get MAX(updated_at) from bronze table
         → fetch only records updated AFTER that timestamp
         Example: last record updated_at = 2024-08-09 22:00:00
         → API call: GET /payments?updated_after=2024-08-09T22:00:00
```

---

## Rate Limit Handling

```
API call
   |
   ├── 200 OK  → parse JSON → transform → insert → commit
   |
   └── 429 Too Many Requests
             → wait 10 seconds
             → retry (up to MAX_RETRIES times)
             → if still failing → log error → skip page
```

---

## Project Folder Structure

```
weekend-project/
├── .env                        ← API credentials, DB config (never commit)
├── .gitignore
├── requirements.txt
├── main.py                     ← pipeline orchestration
├── config/
│   └── settings.py             ← loads .env variables
├── api/
│   └── auth.py                 ← login → get Bearer token
├── etl/
│   ├── extractor.py            ← fetch data from API with pagination
│   ├── transformer.py          ← clean and type-cast raw records
│   └── loader.py               ← insert into PostgreSQL (upsert)
└── tables/
    ├── bronze_all.sql          ← DDL for all bronze tables
    ├── bronze_payments.sql
    └── payments.sql
```

---

## Step-by-Step Build Plan

---

### PHASE 1 — Bronze Layer (DONE ✓)

Everything below is already implemented and working.

---

#### Step 1 — Project Setup ✓

**Files:** `.env`, `requirements.txt`, `config/settings.py`

```
pip install requests psycopg2-binary python-dotenv
```

`.env` holds:
```
API_BASE_URL=https://...
API_USERNAME=...
API_PASSWORD=...
DB_HOST=localhost
DB_PORT=5432
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
PAGE_SIZE=100
REQUEST_DELAY_SEC=0.3
MAX_RETRIES=5
RETRY_BACKOFF_SEC=10
```

`settings.py` loads all values with `os.getenv()`.

---

#### Step 2 — API Authentication ✓

**File:** `api/auth.py`

```python
def get_token(base_url, username, password):
    response = requests.post(f"{base_url}/api/auth/login/",
                             json={"username": username, "password": password})
    return response.json()["token"]
```

- POST credentials → receive Bearer token
- Token is passed as `Authorization: Bearer <token>` in all subsequent calls

---

#### Step 3 — Database Connection ✓

**File:** `database/connection.py`

- Connect to PostgreSQL using psycopg2
- Returns a connection object used across all loaders

---

#### Step 4 — Bronze Schema & Tables ✓

**File:** `etl/loader.py`, `tables/bronze_all.sql`

8 tables in the `bronze` schema:

| Table | Primary Key | Key columns |
|---|---|---|
| `bronze.payments` | `payment_id` | amount, status, updated_at |
| `bronze.sessions` | `session_id` | customer_id, station_id, duration |
| `bronze.customers` | `customer_id` | name, email, city |
| `bronze.vehicles` | `vehicle_id` | make, model, customer_id |
| `bronze.stations` | `station_id` | location, capacity, partner_id |
| `bronze.partners` | `partner_id` | name, contract_start |
| `bronze.energy_prices` | `price_id` | station_id, price_per_kwh |
| `bronze.pipeline_metadata` | `pipeline_name` | last_updated_at, rows_inserted |

All tables have `ingested_at TIMESTAMP` — when the record was loaded.

---

#### Step 5 — Data Extraction ✓

**File:** `etl/extractor.py`

```python
def _fetch(token, endpoint, updated_after=None, max_pages=None):
    page = 1
    all_records = []
    while True:
        params = {"page": page, "page_size": PAGE_SIZE}
        if updated_after:
            params["updated_after"] = updated_after
        response = requests.get(endpoint, headers={"Authorization": f"Bearer {token}"},
                                params=params)
        if response.status_code == 429:
            time.sleep(RETRY_BACKOFF_SEC)
            continue
        data = response.json()
        all_records.extend(data["results"])
        if not data["next"]:
            break
        page += 1
    return all_records
```

7 fetch functions: `fetch_payments`, `fetch_sessions`, `fetch_customers`,
`fetch_vehicles`, `fetch_stations`, `fetch_partners`, `fetch_energy_prices`

---

#### Step 6 — Data Transformation ✓

**File:** `etl/transformer.py`

Each transform function:
- Casts strings to correct types (`float`, `int`, `datetime`)
- Handles missing fields with `.get("field", None)`
- Adds `ingested_at = datetime.utcnow()`

Example:
```python
def transform_payments(raw_records):
    cleaned = []
    for r in raw_records:
        cleaned.append({
            "payment_id":  r.get("id"),
            "amount":      float(r.get("amount", 0)),
            "status":      r.get("status"),
            "updated_at":  r.get("updated_at"),
            "ingested_at": datetime.utcnow()
        })
    return cleaned
```

---

#### Step 7 — Data Loading (Upsert) ✓

**File:** `etl/loader.py`

Uses `INSERT ... ON CONFLICT (pk) DO UPDATE` so re-running the pipeline
never creates duplicates — it updates existing records.

```sql
INSERT INTO bronze.payments (payment_id, amount, status, updated_at, ingested_at)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (payment_id) DO UPDATE SET
    amount      = EXCLUDED.amount,
    status      = EXCLUDED.status,
    updated_at  = EXCLUDED.updated_at,
    ingested_at = EXCLUDED.ingested_at;
```

---

#### Step 8 — Pipeline Metadata Tracking ✓

**File:** `etl/loader.py` → `save_pipeline_metadata()`

After each pipeline run, saves:
- `pipeline_name` (e.g. "payments")
- `last_updated_at` — max updated_at from the loaded records
- `rows_inserted` — count of records loaded
- `run_at` — when the pipeline ran

On the next run, `get_last_updated_at("payments")` reads this to determine the incremental cursor.

---

#### Step 9 — Main Orchestration ✓

**File:** `main.py`

```python
PIPELINES = [
    ("payments",      fetch_payments,      transform_payments,      insert_payments),
    ("sessions",      fetch_sessions,      transform_sessions,      insert_sessions),
    ("customers",     fetch_customers,     transform_customers,     insert_customers),
    ("vehicles",      fetch_vehicles,      transform_vehicles,      insert_vehicles),
    ("stations",      fetch_stations,      transform_stations,      insert_stations),
    ("partners",      fetch_partners,      transform_partners,      insert_partners),
    ("energy_prices", fetch_energy_prices, transform_energy_prices, insert_energy_prices),
]

token = get_token(...)
create_tables(conn)

for name, fetch_fn, transform_fn, insert_fn in PIPELINES:
    last_updated = get_last_updated_at(conn, name)   # None on first run → full load
    raw          = fetch_fn(token, updated_after=last_updated)
    clean        = transform_fn(raw)
    insert_fn(conn, clean)
    save_pipeline_metadata(conn, name, clean)
    conn.commit()
```

---

### PHASE 2 — Production Hardening (TODO)

---

#### Step 10 — Replace print() with logging

**File:** Add at top of every module

**Why:** `print()` has no timestamps, no levels, no log files.
`logging` gives: `2024-08-09 22:05:01 INFO  [payments] Fetched 320 records`

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s [%(name)s] %(message)s",
    handlers=[
        logging.StreamHandler(),                      # print to console
        logging.FileHandler("pipeline.log")           # also write to file
    ]
)
logger = logging.getLogger(__name__)

# Usage
logger.info(f"[{pipeline_name}] Fetched {len(raw)} records")
logger.warning(f"[{pipeline_name}] Rate limited — waiting {RETRY_BACKOFF_SEC}s")
logger.error(f"[{pipeline_name}] Insert failed: {e}")
```

---

#### Step 11 — Error Handling & Dead Letter Table

**Why:** One bad record currently crashes the whole pipeline.
Goal: skip bad records, save them for investigation.

**New table:**
```sql
CREATE TABLE IF NOT EXISTS bronze.failed_records (
    id            SERIAL PRIMARY KEY,
    pipeline_name TEXT,
    raw_record    JSONB,
    error_message TEXT,
    failed_at     TIMESTAMP DEFAULT NOW()
);
```

**Pattern in loader:**
```python
for record in clean_records:
    try:
        cursor.execute(INSERT_SQL, record.values())
    except Exception as e:
        logger.error(f"Failed to insert record {record.get('payment_id')}: {e}")
        save_failed_record(conn, pipeline_name, record, str(e))
        conn.rollback()   # rollback only this record
        conn.autocommit = True
```

---

#### Step 12 — Database Indexes

**Why:** Without indexes, every query on `updated_at` or status does a full table scan.

```sql
-- payments
CREATE INDEX IF NOT EXISTS idx_payments_updated_at ON bronze.payments(updated_at);
CREATE INDEX IF NOT EXISTS idx_payments_status     ON bronze.payments(status);

-- sessions
CREATE INDEX IF NOT EXISTS idx_sessions_customer_id ON bronze.sessions(customer_id);
CREATE INDEX IF NOT EXISTS idx_sessions_station_id  ON bronze.sessions(station_id);
CREATE INDEX IF NOT EXISTS idx_sessions_start_time  ON bronze.sessions(start_time);

-- customers
CREATE INDEX IF NOT EXISTS idx_customers_city ON bronze.customers(city);
```

Add these to `loader.py` → `create_tables()` so they are created automatically.

---

### PHASE 3 — Silver Layer (TODO)

---

#### Step 13 — Silver Schema & Tables

**Why:** Bronze = raw API data (may have nulls, wrong types, test records).
Silver = clean, validated, ready to query.

**Rules applied in Silver:**
- Remove records with NULL on required fields (payment_id, amount, customer_id)
- Remove test/dummy data (e.g. email contains "test" or "dummy")
- Standardize status values to lowercase
- Cast date strings to proper DATE / TIMESTAMP types
- Deduplication — keep latest version of each record

```sql
CREATE SCHEMA IF NOT EXISTS silver;

CREATE TABLE IF NOT EXISTS silver.payments (
    payment_id   TEXT PRIMARY KEY,
    session_id   TEXT,
    customer_id  TEXT,
    amount       NUMERIC(10,2)  NOT NULL,
    currency     TEXT           DEFAULT 'INR',
    status       TEXT           NOT NULL,
    payment_date TIMESTAMP,
    created_at   TIMESTAMP,
    updated_at   TIMESTAMP,
    processed_at TIMESTAMP DEFAULT NOW()
);
```

---

#### Step 14 — Silver Transformation Logic

**File:** `etl/silver_transformer.py`

```python
def silver_payments(bronze_records):
    clean = []
    for r in bronze_records:
        # Drop records missing required fields
        if not r["payment_id"] or not r["amount"]:
            continue
        # Drop test data
        if r.get("customer_id", "").startswith("TEST"):
            continue
        clean.append({
            "payment_id":   r["payment_id"],
            "amount":       round(float(r["amount"]), 2),
            "status":       r["status"].lower().strip(),
            "payment_date": parse_datetime(r.get("payment_date")),
            "updated_at":   parse_datetime(r.get("updated_at")),
            "processed_at": datetime.utcnow()
        })
    return clean
```

---

#### Step 15 — SCD Type 2 for Vehicles (Silver)

**Why:** A vehicle's owner or details can change.
SCD2 keeps the full history — who owned this vehicle and when.

```sql
CREATE TABLE IF NOT EXISTS silver.vehicles_history (
    vehicle_id     TEXT,
    customer_id    TEXT,
    make           TEXT,
    model          TEXT,
    year           INT,
    effective_from DATE NOT NULL,
    effective_to   DATE NOT NULL DEFAULT '9999-12-31',
    is_current     BOOLEAN DEFAULT TRUE
);
```

**Logic (already covered in Day 10):**
- New record for vehicle_id → INSERT with `effective_from = today`, `effective_to = 9999-12-31`
- Vehicle changes owner → close old row (`effective_to = yesterday`, `is_current = false`), insert new row
- No change → keep as-is

---

### PHASE 4 — Gold Layer (TODO)

---

#### Step 16 — Daily Revenue Aggregation

**File:** `etl/gold_aggregator.py`

```sql
CREATE TABLE IF NOT EXISTS gold.daily_revenue AS
SELECT
    DATE(payment_date)       AS revenue_date,
    COUNT(*)                 AS total_transactions,
    SUM(amount)              AS total_revenue,
    AVG(amount)              AS avg_transaction_value,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM silver.payments
WHERE status = 'completed'
GROUP BY DATE(payment_date)
ORDER BY revenue_date;
```

---

#### Step 17 — Station Utilization

```sql
CREATE TABLE IF NOT EXISTS gold.station_utilization AS
SELECT
    s.station_id,
    s.location,
    COUNT(cs.session_id)        AS total_sessions,
    SUM(cs.energy_consumed_kwh) AS total_energy_kwh,
    AVG(cs.duration_minutes)    AS avg_session_duration,
    DATE(cs.start_time)         AS session_date
FROM silver.sessions cs
JOIN silver.stations s ON cs.station_id = s.station_id
GROUP BY s.station_id, s.location, DATE(cs.start_time);
```

---

#### Step 18 — Customer Summary

```sql
CREATE TABLE IF NOT EXISTS gold.customer_summary AS
SELECT
    c.customer_id,
    c.name,
    c.city,
    COUNT(p.payment_id)    AS total_payments,
    SUM(p.amount)          AS lifetime_value,
    MAX(p.payment_date)    AS last_payment_date,
    COUNT(s.session_id)    AS total_sessions
FROM silver.customers c
LEFT JOIN silver.payments p ON c.customer_id = p.customer_id
LEFT JOIN silver.sessions s ON c.customer_id = s.customer_id
GROUP BY c.customer_id, c.name, c.city;
```

---

## Summary: What's Done vs What's Next

| Phase | Step | Description | Status |
|---|---|---|---|
| Bronze | 1 | Project setup & config | Done ✓ |
| Bronze | 2 | API authentication | Done ✓ |
| Bronze | 3 | Database connection | Done ✓ |
| Bronze | 4 | Bronze schema & 8 tables | Done ✓ |
| Bronze | 5 | Data extraction (7 endpoints, pagination, rate limit) | Done ✓ |
| Bronze | 6 | Data transformation (type cast, null handling) | Done ✓ |
| Bronze | 7 | Data loading (upsert with ON CONFLICT) | Done ✓ |
| Bronze | 8 | Pipeline metadata & incremental cursor | Done ✓ |
| Bronze | 9 | Main orchestration loop (all 7 pipelines) | Done ✓ |
| Hardening | 10 | Replace print() with logging module | TODO |
| Hardening | 11 | Error handling + dead letter table | TODO |
| Hardening | 12 | Database indexes for query performance | TODO |
| Silver | 13 | Silver schema & tables | TODO |
| Silver | 14 | Silver transformation (validate, clean, dedup) | TODO |
| Silver | 15 | SCD Type 2 for vehicles history | TODO |
| Gold | 16 | Daily revenue aggregation | TODO |
| Gold | 17 | Station utilization | TODO |
| Gold | 18 | Customer summary (lifetime value) | TODO |
