"""
Day 3 - Reading CSV Files in PySpark
Topics: Reading CSV with all options, inferSchema vs defined schema
        (StructType and DDL string), parse modes, multiple CSV files
"""

import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

os.environ['JAVA_HOME']             = 'C:/Program Files/DBeaver/jre'
os.environ['PYSPARK_PYTHON']        = r'C:\Users\hariom\AppData\Local\Programs\Python\Python311\python.exe'
os.environ['PYSPARK_DRIVER_PYTHON'] = r'C:\Users\hariom\AppData\Local\Programs\Python\Python311\python.exe'

from pyspark.sql import SparkSession

# -------------------------------------------------------
# CSV files used in this session (inside data/)
# -------------------------------------------------------
# employees.csv           - standard CSV with header
# employees_no_header.csv - no header row
# employees_pipe.csv      - pipe (|) separator
# employees_dirty.csv     - missing/bad values
# employees_multiline.csv - values spanning multiple lines
# -------------------------------------------------------

spark = SparkSession.builder \
    .appName("Day3 - Reading CSV") \
    .master("local[*]") \
    .config("spark.sql.shuffle.partitions", "4") \
    .config("spark.ui.showConsoleProgress", "false") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

DATA = "day3-reading-csv-files/data"

print("=" * 60)
print("Day 3 - Reading CSV Files in PySpark")
print("=" * 60)


# =============================================================
# SECTION 1 - READ CSV: basic with inferSchema
# =============================================================
# spark.read.csv() is the entry point for reading CSV files.
#
# inferSchema=True  -> Spark reads the file TWICE:
#                      first pass to sample and detect types,
#                      second pass to load the data.
# header=True       -> first row becomes column names

print("\n--- 1A: CSV with header + inferSchema ---")
df_infer = spark.read.csv(
    f"{DATA}/employees.csv",
    header=True,
    inferSchema=True
)
df_infer.show()
df_infer.printSchema()

print("\n--- 1B: Shorthand format() + load() style ---")
df_fmt = spark.read \
    .format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load(f"{DATA}/employees.csv")
df_fmt.show(3)


# =============================================================
# SECTION 2 - READ CSV: .option() and .options() styles
# =============================================================
# Two ways to pass multiple options:
#   .option("key", "value")            - chain one at a time (readable)
#   .options(key="value", key2="val2") - pass all at once as kwargs

print("\n--- 2A: CSV - chaining .option() calls ---")
df_opts = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .option("dateFormat", "yyyy-MM-dd") \
    .option("nullValue", "N/A") \
    .option("ignoreLeadingWhiteSpace", "true") \
    .option("ignoreTrailingWhiteSpace", "true") \
    .csv(f"{DATA}/employees.csv")
df_opts.show(5)

print("\n--- 2B: CSV - .options() with all kwargs at once ---")
df_opts2 = spark.read \
    .options(header="true", inferSchema="true", nullValue="N/A") \
    .csv(f"{DATA}/employees.csv")
df_opts2.show(5)


# =============================================================
# SECTION 3 - READ CSV: no header row
# =============================================================
# When header=False, Spark auto-names columns: _c0, _c1, _c2 ...
# Use .toDF() to assign proper names after reading.

print("\n--- 3A: No header - auto column names (_c0, _c1 ...) ---")
df_no_hdr = spark.read.csv(
    f"{DATA}/employees_no_header.csv",
    header=False,
    inferSchema=True
)
df_no_hdr.show()

print("\n--- 3B: Rename columns with .toDF() ---")
df_no_hdr = df_no_hdr.toDF(
    "emp_id", "name", "department", "salary", "age", "join_date", "is_active"
)
df_no_hdr.show()


# =============================================================
# SECTION 4 - READ CSV: custom delimiter
# =============================================================
# sep= sets the column separator. Default is comma (,).
# Common values: "|" for pipe, "\t" for tab (TSV), ";" for semicolon.

print("\n--- 4: CSV with pipe (|) separator ---")
df_pipe = spark.read.csv(
    f"{DATA}/employees_pipe.csv",
    header=True,
    inferSchema=True,
    sep="|"
)
df_pipe.show()


# =============================================================
# SECTION 5 - READ CSV: multiline values inside quotes
# =============================================================
# A field value can span multiple lines if it is wrapped in quotes.
# Set multiLine=True so Spark treats it as one value, not two rows.

print("\n--- 5: CSV with multiline quoted field values ---")
df_multi = spark.read.csv(
    f"{DATA}/employees_multiline.csv",
    header=True,
    inferSchema=True,
    multiLine=True,
    quote='"',
    escape='"'
)
df_multi.show(truncate=False)


# =============================================================
# SECTION 6 - READ CSV: dirty data and parse modes
# =============================================================
# Three modes for handling bad/corrupt rows:
#
#   PERMISSIVE   (default) - keeps all rows; bad values become NULL
#   DROPMALFORMED          - silently drops rows that cannot be parsed
#   FAILFAST               - throws exception on the first bad row
#                            (use in production to catch bad data early)

print("\n--- 6A: PERMISSIVE mode (default) + nullValue='N/A' ---")
df_dirty = spark.read.csv(
    f"{DATA}/employees_dirty.csv",
    header=True,
    inferSchema=True,
    nullValue="N/A"
)
df_dirty.show()

print("\n--- 6B: DROPMALFORMED mode ---")
df_drop = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .option("mode", "DROPMALFORMED") \
    .csv(f"{DATA}/employees_dirty.csv")
df_drop.show()

print("\n--- 6C: FAILFAST mode (commented out - throws on bad row) ---")
# df_fail = spark.read \
#     .option("header", "true") \
#     .option("inferSchema", "true") \
#     .option("mode", "FAILFAST") \
#     .csv(f"{DATA}/employees_dirty.csv")
# df_fail.show()
print("    Uncomment above to see the exception on dirty data.")


# =============================================================
# SECTION 7 - DEFINED SCHEMA: StructType
# =============================================================
# New imports: StructType, StructField, type classes
#
# Why define schema explicitly?
#   - Faster : file is read only ONCE (inferSchema reads twice)
#   - Safer  : you control exact types — no guessing
#   - Required in production pipelines

from pyspark.sql.types import (
    StructType, StructField,
    IntegerType, StringType, DoubleType, BooleanType, DateType
)

print("\n--- 7A: Defined schema using StructType ---")
emp_schema = StructType([
    StructField("emp_id",     IntegerType(), True),
    StructField("name",       StringType(),  True),
    StructField("department", StringType(),  True),
    StructField("salary",     DoubleType(),  True),
    StructField("age",        IntegerType(), True),
    StructField("join_date",  DateType(),    True),
    StructField("is_active",  BooleanType(), True),
])

df_schema = spark.read \
    .schema(emp_schema) \
    .option("header", "true") \
    .option("dateFormat", "yyyy-MM-dd") \
    .csv(f"{DATA}/employees.csv")
df_schema.show()
df_schema.printSchema()

print("\n--- 7B: DDL schema string (shortcut) ---")
# Same result as StructType above but written as a SQL DDL string.
# Faster to type, easier to read for simple schemas.
ddl = "emp_id INT, name STRING, department STRING, salary DOUBLE, age INT, join_date DATE, is_active BOOLEAN"

df_ddl = spark.read \
    .schema(ddl) \
    .option("header", "true") \
    .option("dateFormat", "yyyy-MM-dd") \
    .csv(f"{DATA}/employees.csv")
df_ddl.show()
df_ddl.printSchema()

print("\n--- 7C: Defined schema + no header (column order matters!) ---")
df_schema_nohdr = spark.read \
    .schema(ddl) \
    .option("header", "false") \
    .csv(f"{DATA}/employees_no_header.csv")
df_schema_nohdr.show()


# =============================================================
# SECTION 8 - READ MULTIPLE CSV FILES
# =============================================================
# New import: input_file_name (from pyspark.sql.functions)
#
# Three ways to read multiple files:
#   list of paths  - explicit, works on ALL platforms including Windows
#   folder path    - reads all CSVs in folder (Linux/Mac/Databricks)
#   wildcard       - pattern match (Linux/Mac/Databricks)

from pyspark.sql.functions import input_file_name

print("\n--- 8A: List of specific files (works on all platforms) ---")
df_list = spark.read.csv(
    [f"{DATA}/employees.csv", f"{DATA}/employees_no_header.csv"],
    header=True,
    inferSchema=True
)
print(f"Total rows: {df_list.count()}")
df_list.show(5)

print("\n--- 8B: Folder and wildcard (Linux/Mac/Databricks only) ---")
print("    spark.read.csv('data/', header=True)             -- all CSVs in folder")
print("    spark.read.csv('data/employees_*.csv', ...)      -- wildcard pattern")

print("\n--- 8C: input_file_name() - trace which file each row came from ---")
df_src = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv([f"{DATA}/employees.csv", f"{DATA}/employees_no_header.csv"]) \
    .withColumn("source_file", input_file_name())
df_src.select("emp_id", "name", "source_file").show(10, truncate=False)


# =============================================================
# SECTION 9 - WRITE CSV (reference)
# =============================================================
# Writing requires native Hadoop on Windows.
# Works on Linux/Mac/Databricks without any setup.
#
# Spark writes a FOLDER, not a single file.
# Each partition produces one part-*.csv file inside the folder.

print("\n--- 9: Write modes reference ---")
print("    overwrite : delete existing data and write fresh")
print("    append    : add to existing data")
print("    ignore    : skip write if path already exists")
print("    error     : throw exception if path already exists (default)")
print("")
print("    df.write.mode('overwrite').option('header','true').csv('output/emp')")

# Uncomment on Linux/Mac/Databricks:
# df_schema.write \
#     .mode("overwrite") \
#     .option("header", "true") \
#     .csv("pyspark-sessions/day3-reading-files/output/employees_csv")


# =============================================================
# IMPORTS SUMMARY
# =============================================================
# from pyspark.sql import SparkSession                 -- always needed
# Section 7: from pyspark.sql.types import
#               StructType, StructField, IntegerType,
#               StringType, DoubleType, BooleanType, DateType
# Section 8: from pyspark.sql.functions import input_file_name

print("\n" + "=" * 60)
print("Day 3 Complete - CSV Reading")
print("=" * 60)

spark.stop()
print("SparkSession stopped. Done.")
