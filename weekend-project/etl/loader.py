import json
from datetime import datetime, timezone
from config.logger import get_logger

logger = get_logger("loader")


# ── Schema + all tables setup ────────────────────────────────────────────────

def create_tables(connection):
    cursor = connection.cursor()

    cursor.execute("CREATE SCHEMA IF NOT EXISTS bronze;")

    # payments
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bronze.payments (
            id            BIGINT PRIMARY KEY,
            payment_id    VARCHAR(100) UNIQUE NOT NULL,
            session_id    VARCHAR(100),
            customer_id   VARCHAR(100),
            gateway       VARCHAR(50),
            amount_aud    NUMERIC(12, 2),
            gst           NUMERIC(12, 2),
            payment_mode  VARCHAR(50),
            status        VARCHAR(50),
            processed_at  TIMESTAMPTZ,
            created_at    TIMESTAMPTZ,
            updated_at    TIMESTAMPTZ,
            ingested_at   TIMESTAMPTZ
        );
    """)

    # charging sessions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bronze.sessions (
            id             BIGINT PRIMARY KEY,
            session_id     VARCHAR(100) UNIQUE NOT NULL,
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
            created_at     TIMESTAMPTZ,
            updated_at     TIMESTAMPTZ,
            ingested_at    TIMESTAMPTZ
        );
    """)

    # customers
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bronze.customers (
            id            BIGINT PRIMARY KEY,
            customer_id   VARCHAR(100) UNIQUE NOT NULL,
            full_name     VARCHAR(200),
            email         VARCHAR(200),
            phone         VARCHAR(50),
            loyalty_tier  VARCHAR(50),
            signup_date   DATE,
            created_at    TIMESTAMPTZ,
            updated_at    TIMESTAMPTZ,
            ingested_at   TIMESTAMPTZ
        );
    """)

    # vehicles (SCD2 — multiple rows per vehicle_id for history)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bronze.vehicles (
            id                   BIGINT PRIMARY KEY,
            vehicle_id           VARCHAR(100) NOT NULL,
            make                 VARCHAR(100),
            model                VARCHAR(100),
            year                 INT,
            vehicle_type         VARCHAR(20),
            battery_capacity_kwh NUMERIC(8, 2),
            range_km             INT,
            registration_state   VARCHAR(10),
            partner_id           VARCHAR(100),
            effective_from       DATE,
            effective_to         DATE,
            is_current           BOOLEAN,
            created_at           TIMESTAMPTZ,
            updated_at           TIMESTAMPTZ,
            ingested_at          TIMESTAMPTZ
        );
    """)

    # charging stations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bronze.stations (
            id                 BIGINT PRIMARY KEY,
            station_id         VARCHAR(100) UNIQUE NOT NULL,
            name               VARCHAR(200),
            state_code         VARCHAR(10),
            city               VARCHAR(100),
            latitude           NUMERIC(10, 6),
            longitude          NUMERIC(10, 6),
            charger_type       VARCHAR(50),
            max_power_kw       NUMERIC(8, 2),
            num_connectors     INT,
            operator           VARCHAR(100),
            is_active          BOOLEAN,
            commissioned_date  DATE,
            created_at         TIMESTAMPTZ,
            updated_at         TIMESTAMPTZ,
            ingested_at        TIMESTAMPTZ
        );
    """)

    # partners
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bronze.partners (
            id                 BIGINT PRIMARY KEY,
            partner_id         VARCHAR(100) UNIQUE NOT NULL,
            partner_name       VARCHAR(200),
            state              VARCHAR(50),
            status             VARCHAR(50),
            revenue_share_pct  NUMERIC(5, 2),
            contract_start     DATE,
            contract_end       DATE,
            created_at         TIMESTAMPTZ,
            updated_at         TIMESTAMPTZ,
            ingested_at        TIMESTAMPTZ
        );
    """)

    # energy prices
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bronze.energy_prices (
            id              BIGINT PRIMARY KEY,
            price_id        VARCHAR(100) UNIQUE NOT NULL,
            station_id      VARCHAR(100),
            state_code      VARCHAR(10),
            price_per_kwh   NUMERIC(8, 4),
            off_peak_price  NUMERIC(8, 4),
            peak_price      NUMERIC(8, 4),
            currency        VARCHAR(10),
            tariff_type     VARCHAR(50),
            effective_from  TIMESTAMPTZ,
            effective_to    TIMESTAMPTZ,
            created_at      TIMESTAMPTZ,
            updated_at      TIMESTAMPTZ,
            ingested_at     TIMESTAMPTZ
        );
    """)

    # pipeline metadata — tracks last run per pipeline for incremental load
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bronze.pipeline_metadata (
            id                SERIAL PRIMARY KEY,
            pipeline_name     VARCHAR(100),
            load_type         VARCHAR(20),
            last_run_at       TIMESTAMPTZ,
            last_updated_at   TIMESTAMPTZ,
            records_inserted  INT
        );
    """)

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

    # ── Indexes for query performance ────────────────────────────────────────
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

    connection.commit()
    logger.info("All bronze tables and indexes created/verified")


# ── Metadata helpers ─────────────────────────────────────────────────────────

def get_last_updated_at(connection, pipeline_name):
    cursor = connection.cursor()
    cursor.execute("""
        SELECT last_updated_at
        FROM bronze.pipeline_metadata
        WHERE pipeline_name = %s
        ORDER BY last_run_at DESC
        LIMIT 1;
    """, (pipeline_name,))
    row = cursor.fetchone()
    if row and row[0]:
        return row[0].isoformat()
    return None


def save_pipeline_metadata(connection, pipeline_name, load_type, records_inserted, last_updated_at):
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO bronze.pipeline_metadata
            (pipeline_name, load_type, last_run_at, last_updated_at, records_inserted)
        VALUES (%s, %s, %s, %s, %s);
    """, (
        pipeline_name,
        load_type,
        datetime.now(timezone.utc),
        last_updated_at,
        records_inserted
    ))
    connection.commit()
    logger.info(f"Metadata saved for {pipeline_name} — {records_inserted} records")


# ── Dead letter helper ────────────────────────────────────────────────────────

def save_failed_record(connection, pipeline_name, record, error_message):
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO bronze.failed_records (pipeline_name, raw_record, error_message)
        VALUES (%s, %s, %s);
    """, (pipeline_name, json.dumps(record, default=str), error_message))
    connection.commit()
    logger.warning(f"Failed record saved for pipeline '{pipeline_name}': {error_message}")


# ── Insert functions — one per table ─────────────────────────────────────────

def insert_payments(connection, records):
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
    success, failed = 0, 0
    for record in records:
        try:
            connection.cursor().execute(query, record)
            connection.commit()
            success += 1
        except Exception as e:
            connection.rollback()
            failed += 1
            logger.error(f"Insert failed for payment_id {record.get('payment_id')}: {e}")
            save_failed_record(connection, "payments", record, str(e))
    logger.info(f"bronze.payments — inserted: {success}, failed: {failed}")


def insert_sessions(connection, records):
    query = """
        INSERT INTO bronze.sessions (
            id, session_id, vehicle_id, station_id, customer_id,
            started_at, ended_at, duration_min, energy_kwh, cost_aud,
            peak_power_kw, connector_type, session_status, payment_id,
            created_at, updated_at, ingested_at
        ) VALUES (
            %(id)s, %(session_id)s, %(vehicle_id)s, %(station_id)s, %(customer_id)s,
            %(started_at)s, %(ended_at)s, %(duration_min)s, %(energy_kwh)s, %(cost_aud)s,
            %(peak_power_kw)s, %(connector_type)s, %(session_status)s, %(payment_id)s,
            %(created_at)s, %(updated_at)s, %(ingested_at)s
        )
        ON CONFLICT (id) DO UPDATE SET
            session_status = EXCLUDED.session_status,
            energy_kwh     = EXCLUDED.energy_kwh,
            cost_aud       = EXCLUDED.cost_aud,
            updated_at     = EXCLUDED.updated_at,
            ingested_at    = EXCLUDED.ingested_at;
    """
    success, failed = 0, 0
    for record in records:
        try:
            connection.cursor().execute(query, record)
            connection.commit()
            success += 1
        except Exception as e:
            connection.rollback()
            failed += 1
            logger.error(f"Insert failed for session_id {record.get('session_id')}: {e}")
            save_failed_record(connection, "sessions", record, str(e))
    logger.info(f"bronze.sessions — inserted: {success}, failed: {failed}")


def insert_customers(connection, records):
    query = """
        INSERT INTO bronze.customers (
            id, customer_id, full_name, email, phone,
            loyalty_tier, signup_date, created_at, updated_at, ingested_at
        ) VALUES (
            %(id)s, %(customer_id)s, %(full_name)s, %(email)s, %(phone)s,
            %(loyalty_tier)s, %(signup_date)s, %(created_at)s, %(updated_at)s, %(ingested_at)s
        )
        ON CONFLICT (id) DO UPDATE SET
            loyalty_tier = EXCLUDED.loyalty_tier,
            email        = EXCLUDED.email,
            updated_at   = EXCLUDED.updated_at,
            ingested_at  = EXCLUDED.ingested_at;
    """
    success, failed = 0, 0
    for record in records:
        try:
            connection.cursor().execute(query, record)
            connection.commit()
            success += 1
        except Exception as e:
            connection.rollback()
            failed += 1
            logger.error(f"Insert failed for customer_id {record.get('customer_id')}: {e}")
            save_failed_record(connection, "customers", record, str(e))
    logger.info(f"bronze.customers — inserted: {success}, failed: {failed}")


def insert_vehicles(connection, records):
    query = """
        INSERT INTO bronze.vehicles (
            id, vehicle_id, make, model, year, vehicle_type,
            battery_capacity_kwh, range_km, registration_state, partner_id,
            effective_from, effective_to, is_current,
            created_at, updated_at, ingested_at
        ) VALUES (
            %(id)s, %(vehicle_id)s, %(make)s, %(model)s, %(year)s, %(vehicle_type)s,
            %(battery_capacity_kwh)s, %(range_km)s, %(registration_state)s, %(partner_id)s,
            %(effective_from)s, %(effective_to)s, %(is_current)s,
            %(created_at)s, %(updated_at)s, %(ingested_at)s
        )
        ON CONFLICT (id) DO UPDATE SET
            is_current           = EXCLUDED.is_current,
            effective_to         = EXCLUDED.effective_to,
            battery_capacity_kwh = EXCLUDED.battery_capacity_kwh,
            updated_at           = EXCLUDED.updated_at,
            ingested_at          = EXCLUDED.ingested_at;
    """
    success, failed = 0, 0
    for record in records:
        try:
            connection.cursor().execute(query, record)
            connection.commit()
            success += 1
        except Exception as e:
            connection.rollback()
            failed += 1
            logger.error(f"Insert failed for vehicle_id {record.get('vehicle_id')}: {e}")
            save_failed_record(connection, "vehicles", record, str(e))
    logger.info(f"bronze.vehicles — inserted: {success}, failed: {failed}")


def insert_stations(connection, records):
    query = """
        INSERT INTO bronze.stations (
            id, station_id, name, state_code, city,
            latitude, longitude, charger_type, max_power_kw,
            num_connectors, operator, is_active, commissioned_date,
            created_at, updated_at, ingested_at
        ) VALUES (
            %(id)s, %(station_id)s, %(name)s, %(state_code)s, %(city)s,
            %(latitude)s, %(longitude)s, %(charger_type)s, %(max_power_kw)s,
            %(num_connectors)s, %(operator)s, %(is_active)s, %(commissioned_date)s,
            %(created_at)s, %(updated_at)s, %(ingested_at)s
        )
        ON CONFLICT (id) DO UPDATE SET
            is_active   = EXCLUDED.is_active,
            operator    = EXCLUDED.operator,
            updated_at  = EXCLUDED.updated_at,
            ingested_at = EXCLUDED.ingested_at;
    """
    success, failed = 0, 0
    for record in records:
        try:
            connection.cursor().execute(query, record)
            connection.commit()
            success += 1
        except Exception as e:
            connection.rollback()
            failed += 1
            logger.error(f"Insert failed for station_id {record.get('station_id')}: {e}")
            save_failed_record(connection, "stations", record, str(e))
    logger.info(f"bronze.stations — inserted: {success}, failed: {failed}")


def insert_partners(connection, records):
    query = """
        INSERT INTO bronze.partners (
            id, partner_id, partner_name, state, status,
            revenue_share_pct, contract_start, contract_end,
            created_at, updated_at, ingested_at
        ) VALUES (
            %(id)s, %(partner_id)s, %(partner_name)s, %(state)s, %(status)s,
            %(revenue_share_pct)s, %(contract_start)s, %(contract_end)s,
            %(created_at)s, %(updated_at)s, %(ingested_at)s
        )
        ON CONFLICT (id) DO UPDATE SET
            status            = EXCLUDED.status,
            revenue_share_pct = EXCLUDED.revenue_share_pct,
            updated_at        = EXCLUDED.updated_at,
            ingested_at       = EXCLUDED.ingested_at;
    """
    success, failed = 0, 0
    for record in records:
        try:
            connection.cursor().execute(query, record)
            connection.commit()
            success += 1
        except Exception as e:
            connection.rollback()
            failed += 1
            logger.error(f"Insert failed for partner_id {record.get('partner_id')}: {e}")
            save_failed_record(connection, "partners", record, str(e))
    logger.info(f"bronze.partners — inserted: {success}, failed: {failed}")


def insert_energy_prices(connection, records):
    query = """
        INSERT INTO bronze.energy_prices (
            id, price_id, station_id, state_code,
            price_per_kwh, off_peak_price, peak_price,
            currency, tariff_type, effective_from, effective_to,
            created_at, updated_at, ingested_at
        ) VALUES (
            %(id)s, %(price_id)s, %(station_id)s, %(state_code)s,
            %(price_per_kwh)s, %(off_peak_price)s, %(peak_price)s,
            %(currency)s, %(tariff_type)s, %(effective_from)s, %(effective_to)s,
            %(created_at)s, %(updated_at)s, %(ingested_at)s
        )
        ON CONFLICT (id) DO UPDATE SET
            price_per_kwh  = EXCLUDED.price_per_kwh,
            peak_price     = EXCLUDED.peak_price,
            effective_to   = EXCLUDED.effective_to,
            updated_at     = EXCLUDED.updated_at,
            ingested_at    = EXCLUDED.ingested_at;
    """
    success, failed = 0, 0
    for record in records:
        try:
            connection.cursor().execute(query, record)
            connection.commit()
            success += 1
        except Exception as e:
            connection.rollback()
            failed += 1
            logger.error(f"Insert failed for price_id {record.get('price_id')}: {e}")
            save_failed_record(connection, "energy_prices", record, str(e))
    logger.info(f"bronze.energy_prices — inserted: {success}, failed: {failed}")
