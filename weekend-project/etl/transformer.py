from datetime import datetime, timezone
from config.logger import get_logger

logger = get_logger("transformer")


def _now():
    return datetime.now(timezone.utc).isoformat()


# ── Payments ─────────────────────────────────────────────────────────────────

def transform_payments(records):
    clean_records = []
    for record in records:
        clean = {
            "id"          : record["id"],
            "payment_id"  : record["payment_id"],
            "session_id"  : record["session_id"],
            "customer_id" : record["customer_id"],
            "gateway"     : record["gateway"],
            "amount_aud"  : float(record["amount_aud"]),
            "gst"         : float(record["gst"]),
            "payment_mode": record["payment_mode"],
            "status"      : record["status"],
            "processed_at": record["processed_at"],
            "created_at"  : record["created_at"],
            "updated_at"  : record["updated_at"],
            "ingested_at" : _now(),
        }
        clean_records.append(clean)
    logger.info(f"Transformed {len(clean_records)} payment records")
    return clean_records


# ── Charging Sessions ─────────────────────────────────────────────────────────

def transform_sessions(records):
    clean_records = []
    for record in records:
        clean = {
            "id"            : record["id"],
            "session_id"    : record["session_id"],
            "vehicle_id"    : record["vehicle_id"],
            "station_id"    : record["station_id"],
            "customer_id"   : record["customer_id"],
            "started_at"    : record["started_at"],
            "ended_at"      : record["ended_at"],
            "duration_min"  : record.get("duration_min"),
            "energy_kwh"    : float(record["energy_kwh"]) if record.get("energy_kwh") else None,
            "cost_aud"      : float(record["cost_aud"]) if record.get("cost_aud") else None,
            "peak_power_kw" : float(record["peak_power_kw"]) if record.get("peak_power_kw") else None,
            "connector_type": record.get("connector_type"),
            "session_status": record.get("session_status"),
            "payment_id"    : record.get("payment_id"),
            "created_at"    : record["created_at"],
            "updated_at"    : record["updated_at"],
            "ingested_at"   : _now(),
        }
        clean_records.append(clean)
    logger.info(f"Transformed {len(clean_records)} session records")
    return clean_records


# ── Customers ─────────────────────────────────────────────────────────────────

def transform_customers(records):
    clean_records = []
    for record in records:
        clean = {
            "id"           : record["id"],
            "customer_id"  : record["customer_id"],
            "full_name"    : record["full_name"],
            "email"        : record["email"],
            "phone"        : record.get("phone"),
            "loyalty_tier" : record.get("loyalty_tier"),
            "signup_date"  : record.get("signup_date"),
            "created_at"   : record["created_at"],
            "updated_at"   : record["updated_at"],
            "ingested_at"  : _now(),
        }
        clean_records.append(clean)
    logger.info(f"Transformed {len(clean_records)} customer records")
    return clean_records


# ── Vehicles ──────────────────────────────────────────────────────────────────

def transform_vehicles(records):
    clean_records = []
    for record in records:
        clean = {
            "id"                  : record["id"],
            "vehicle_id"          : record["vehicle_id"],
            "make"                : record["make"],
            "model"               : record["model"],
            "year"                : record["year"],
            "vehicle_type"        : record.get("vehicle_type"),
            "battery_capacity_kwh": float(record["battery_capacity_kwh"]) if record.get("battery_capacity_kwh") else None,
            "range_km"            : record.get("range_km"),
            "registration_state"  : record.get("registration_state"),
            "partner_id"          : record.get("partner_id"),
            "effective_from"      : record.get("effective_from"),
            "effective_to"        : record.get("effective_to"),
            "is_current"          : record.get("is_current", True),
            "created_at"          : record["created_at"],
            "updated_at"          : record["updated_at"],
            "ingested_at"         : _now(),
        }
        clean_records.append(clean)
    logger.info(f"Transformed {len(clean_records)} vehicle records")
    return clean_records


# ── Charging Stations ─────────────────────────────────────────────────────────

def transform_stations(records):
    clean_records = []
    for record in records:
        clean = {
            "id"                : record["id"],
            "station_id"        : record["station_id"],
            "name"              : record.get("name"),
            "state_code"        : record.get("state_code"),
            "city"              : record.get("city"),
            "latitude"          : float(record["latitude"]) if record.get("latitude") else None,
            "longitude"         : float(record["longitude"]) if record.get("longitude") else None,
            "charger_type"      : record.get("charger_type"),
            "max_power_kw"      : float(record["max_power_kw"]) if record.get("max_power_kw") else None,
            "num_connectors"    : record.get("num_connectors"),
            "operator"          : record.get("operator"),
            "is_active"         : record.get("is_active", True),
            "commissioned_date" : record.get("commissioned_date"),
            "created_at"        : record["created_at"],
            "updated_at"        : record["updated_at"],
            "ingested_at"       : _now(),
        }
        clean_records.append(clean)
    logger.info(f"Transformed {len(clean_records)} station records")
    return clean_records


# ── Partners ──────────────────────────────────────────────────────────────────

def transform_partners(records):
    clean_records = []
    for record in records:
        clean = {
            "id"                 : record["id"],
            "partner_id"         : record["partner_id"],
            "partner_name"       : record["partner_name"],
            "state"              : record.get("state"),
            "status"             : record.get("status"),
            "revenue_share_pct"  : float(record["revenue_share_pct"]) if record.get("revenue_share_pct") else None,
            "contract_start"     : record.get("contract_start"),
            "contract_end"       : record.get("contract_end"),
            "created_at"         : record["created_at"],
            "updated_at"         : record["updated_at"],
            "ingested_at"        : _now(),
        }
        clean_records.append(clean)
    logger.info(f"Transformed {len(clean_records)} partner records")
    return clean_records


# ── Energy Prices ─────────────────────────────────────────────────────────────

def transform_energy_prices(records):
    clean_records = []
    for record in records:
        clean = {
            "id"              : record["id"],
            "price_id"        : record["price_id"],
            "station_id"      : record.get("station_id"),
            "state_code"      : record.get("state_code"),
            "price_per_kwh"   : float(record["price_per_kwh"]) if record.get("price_per_kwh") else None,
            "off_peak_price"  : float(record["off_peak_price"]) if record.get("off_peak_price") else None,
            "peak_price"      : float(record["peak_price"]) if record.get("peak_price") else None,
            "currency"        : record.get("currency", "AUD"),
            "tariff_type"     : record.get("tariff_type"),
            "effective_from"  : record.get("effective_from"),
            "effective_to"    : record.get("effective_to"),
            "created_at"      : record["created_at"],
            "updated_at"      : record["updated_at"],
            "ingested_at"     : _now(),
        }
        clean_records.append(clean)
    logger.info(f"Transformed {len(clean_records)} energy price records")
    return clean_records
