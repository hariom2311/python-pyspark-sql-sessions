"""
config/db_config.py
-------------------
Central configuration for the Retail Analytics DE Project.
Every notebook imports this file via:

    import sys, os
    sys.path.insert(0, os.path.join(os.getcwd(), '..'))
    from config.db_config import *

Provides:
  - DB credentials + SQLAlchemy engine
  - PySpark environment variables (set before any pyspark import)
  - SparkSession factory
  - Schema bootstrap (bronze / silver / gold)
  - Shared batch metadata helpers
"""

import os
import uuid
from datetime import datetime
from sqlalchemy import create_engine, text

# ── PostgreSQL credentials ─────────────────────────────────────────────────────
DB_USER = "postgres"
DB_PASS = "hariom"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "postgres"

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def get_engine():
    """Return a SQLAlchemy engine connected to PostgreSQL."""
    return create_engine(DATABASE_URL, echo=False)


def ensure_schemas(engine=None):
    """Create bronze / silver / gold schemas if they don't already exist."""
    eng = engine or get_engine()
    with eng.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS bronze;"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS silver;"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS gold;"))
        conn.commit()
    print("[db_config] Schemas bronze / silver / gold are ready.")


# ── PySpark environment ────────────────────────────────────────────────────────
# Must be set BEFORE any pyspark import.
# Call set_spark_env() at the top of any notebook that uses PySpark.
def set_spark_env():
    """
    Set JAVA_HOME and PYSPARK_* env vars so the Spark worker always uses
    the same Python that is currently running (the active kernel/venv).

    This is auto-detected via sys.executable — no hardcoded paths.
    Students don't need to change anything; it works with any Python version
    as long as PySpark is installed in the active environment.

    JAVA_HOME: auto-detected from 'java' on PATH, then common install locations.
    Override by setting JAVA_HOME in your OS environment before launching Jupyter.
    """
    import sys
    import shutil

    # ── Python: always use the currently running interpreter ───────────────────
    current_python = sys.executable
    os.environ["PYSPARK_PYTHON"]        = current_python
    os.environ["PYSPARK_DRIVER_PYTHON"] = current_python

    # ── JAVA_HOME: auto-detect (skip if already set) ───────────────────────────
    if not os.environ.get("JAVA_HOME"):
        java_exe = shutil.which("java")
        if java_exe:
            # java is at <JAVA_HOME>/bin/java  →  go up two levels
            java_home = os.path.dirname(os.path.dirname(os.path.realpath(java_exe)))
            os.environ["JAVA_HOME"] = java_home
        else:
            # Fallback: common locations on Windows / macOS / Linux
            candidates = [
                r"C:\Program Files\DBeaver\jre",
                r"C:\Program Files\Java\jdk-11",
                r"C:\Program Files\Microsoft\jdk-11.0.16.8-hotspot",
                "/usr/lib/jvm/java-11-openjdk-amd64",
                "/usr/lib/jvm/java-11-openjdk",
                "/Library/Java/JavaVirtualMachines/temurin-11.jdk/Contents/Home",
            ]
            for c in candidates:
                if os.path.isdir(c):
                    os.environ["JAVA_HOME"] = c
                    break

    java_home = os.environ.get("JAVA_HOME", "(not found — set JAVA_HOME manually)")
    print(f"[db_config] PYSPARK_PYTHON        = {current_python}")
    print(f"[db_config] JAVA_HOME             = {java_home}")
    print("[db_config] Spark environment variables set.")


def _find_pg_jar():
    """
    Locate the PostgreSQL JDBC jar.

    Search order (first match wins):
      1. pyspark/jars/ of the currently-running Python interpreter
      2. pyspark/jars/ inside the project-local venv (myenv / venv / .venv / env)
      3. Any pyspark/jars/ reachable from sys.path
    """
    import sys
    import glob
    import importlib.util

    jar_name = "postgresql-*.jar"

    # 1. pyspark installed in the running interpreter (most reliable)
    spec = importlib.util.find_spec("pyspark")
    if spec and spec.origin:
        jars_dir = os.path.join(os.path.dirname(spec.origin), "jars")
        matches = glob.glob(os.path.join(jars_dir, jar_name))
        if matches:
            return matches[0]

    # 2. project-local venv — relative to this config file
    #    db_config.py is at <project>/config/db_config.py
    #    venv is at      <project>/myenv/  (or venv / .venv / env)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for venv_dir in ("myenv", "venv", ".venv", "env"):
        for lib in ("Lib", "lib"):
            pattern = os.path.join(project_root, venv_dir, lib,
                                   "site-packages", "pyspark", "jars", jar_name)
            matches = glob.glob(pattern)
            if matches:
                return matches[0]

    # 3. scan every sys.path entry
    for p in sys.path:
        matches = glob.glob(os.path.join(p, "pyspark", "jars", jar_name))
        if matches:
            return matches[0]

    raise FileNotFoundError(
        "\n\nPostgreSQL JDBC jar not found.\n\n"
        "Run this ONE-TIME command in your terminal with the venv activated:\n\n"
        "  Windows (PowerShell):\n"
        "    $d = python -c \"import pyspark,os; print(os.path.join(os.path.dirname(pyspark.__file__),'jars'))\"\n"
        "    Invoke-WebRequest https://jdbc.postgresql.org/download/postgresql-42.7.3.jar -OutFile \"$d\\postgresql-42.7.3.jar\"\n\n"
        "  macOS / Linux:\n"
        "    JAR_DIR=$(python -c \"import pyspark,os; print(os.path.join(os.path.dirname(pyspark.__file__),'jars'))\")\n"
        "    curl -L https://jdbc.postgresql.org/download/postgresql-42.7.3.jar -o \"$JAR_DIR/postgresql-42.7.3.jar\"\n\n"
        "Then restart the Jupyter kernel.\n"
    )


def get_spark(app_name: str = "RetailDE"):
    """
    Return a local SparkSession with the PostgreSQL JDBC jar on the classpath.
    Always call set_spark_env() before this function.

    The JDBC jar is auto-detected from the active PySpark installation — no
    hardcoded paths. If PySpark is not installed in the active kernel, a clear
    message tells you which kernel to switch to.
    """
    import sys
    import importlib.util

    # Check PySpark is importable in this kernel before trying anything else
    if importlib.util.find_spec("pyspark") is None:
        raise EnvironmentError(
            f"\n\nPySpark is NOT installed in the current Python kernel:\n"
            f"  {sys.executable}\n\n"
            f"Fix: In Jupyter, go to  Kernel → Change Kernel\n"
            f"and select the kernel whose name matches your virtual environment\n"
            f"(e.g. 'myenv', 'Python 3 (ipykernel)', or 'Python 3.11').\n\n"
            f"That environment already has PySpark installed.\n"
            f"Do NOT use the bare 'Python 3' system kernel.\n"
        )

    pg_jar = _find_pg_jar()

    from pyspark.sql import SparkSession
    spark = (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.ui.showConsoleProgress", "false")
        .config("spark.driver.extraClassPath", pg_jar)
        .config("spark.executor.extraClassPath", pg_jar)
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    print(f"[db_config] Spark {spark.version} ready — app: {app_name}")
    print(f"[db_config] JDBC jar: {pg_jar}")
    return spark


# ── Shared batch metadata ──────────────────────────────────────────────────────
def new_batch():
    """Return (BATCH_ID, INGESTED_AT) for tagging bronze rows."""
    return str(uuid.uuid4()), datetime.utcnow().isoformat()


# ── Raw data path helper ───────────────────────────────────────────────────────
def raw_path(*parts):
    """
    Build path to data/raw relative to this config file.
    Usage: raw_path('customers.csv')  →  '<project>/data/raw/customers.csv'
    """
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "data", "raw", *parts)


# ── JDBC write helper ──────────────────────────────────────────────────────────
JDBC_URL = f"jdbc:postgresql://{DB_HOST}:{DB_PORT}/{DB_NAME}"

def spark_write_pg(df, schema, table, mode="overwrite"):
    """
    Write a PySpark DataFrame to PostgreSQL via JDBC.

    Usage:
        spark_write_pg(df, 'bronze', 'customers')
        spark_write_pg(df, 'silver', 'orders', mode='overwrite')
    """
    (
        df.write
        .format("jdbc")
        .option("url",           JDBC_URL)
        .option("dbtable",       f"{schema}.{table}")
        .option("user",          DB_USER)
        .option("password",      DB_PASS)
        .option("driver",        "org.postgresql.Driver")
        .option("currentSchema", schema)
        .mode(mode)
        .save()
    )
    print(f"  {schema}.{table:<26} → {df.count():>5} rows  [{mode}]")


# ── JDBC read helper ───────────────────────────────────────────────────────────
def spark_read_pg(spark, schema, table):
    """
    Read a PostgreSQL table into a PySpark DataFrame via JDBC.

    Usage:
        df = spark_read_pg(spark, 'bronze', 'customers')
    """
    return (
        spark.read
        .format("jdbc")
        .option("url",           JDBC_URL)
        .option("dbtable",       f"{schema}.{table}")
        .option("user",          DB_USER)
        .option("password",      DB_PASS)
        .option("driver",        "org.postgresql.Driver")
        .option("currentSchema", schema)
        .load()
    )
