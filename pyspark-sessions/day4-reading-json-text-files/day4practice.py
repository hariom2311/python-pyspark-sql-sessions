"""
Day 4 - Reading JSON and Text Files in PySpark
Topics: Flat JSONL, multi-line JSON array, nested struct, array fields,
        explode, from_json, get_json_object, json_tuple, text + regexp_extract
"""

import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

os.environ['JAVA_HOME']             = 'C:/Program Files/DBeaver/jre'
os.environ['PYSPARK_PYTHON']        = r'C:\Users\hariom\AppData\Local\Programs\Python\Python311\python.exe'
os.environ['PYSPARK_DRIVER_PYTHON'] = r'C:\Users\hariom\AppData\Local\Programs\Python\Python311\python.exe'

from pyspark.sql import SparkSession

# -------------------------------------------------------
# Files used in this session (inside data/)
# -------------------------------------------------------
# employees_flat.json     - one JSON object per line (JSONL)
# employees_nested.json   - nested struct + array field (skills)
# employees_array.json    - whole file is one JSON array [...]
# orders.json             - array of item structs per order
# logs.txt                - raw unstructured log lines
# -------------------------------------------------------

spark = SparkSession.builder \
    .appName("Day4 - Reading JSON and Text") \
    .master("local[*]") \
    .config("spark.sql.shuffle.partitions", "4") \
    .config("spark.ui.showConsoleProgress", "false") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

DATA = "day4-reading-json-text-files/data"

print("=" * 60)
print("Day 4 - Reading JSON and Text Files in PySpark")
print("=" * 60)


# =============================================================
# SECTION 1 - READ JSON: flat JSONL (one object per line)
# =============================================================
# Spark's default JSON reader expects JSONL format:
#   each line is one complete, self-contained JSON object.
#
# {"id": 1, "name": "Alice"}
# {"id": 2, "name": "Bob"}
#
# Columns are sorted ALPHABETICALLY when schema is inferred.
# Use an explicit schema to control column order and types.

print("\n--- 1A: Flat JSONL - inferSchema ---")
df_json = spark.read.json(f"{DATA}/employees_flat.json")
df_json.show()
df_json.printSchema()

print("\n--- 1B: Flat JSONL - explicit StructType schema ---")
from pyspark.sql.types import (
    StructType, StructField,
    IntegerType, StringType, DoubleType, BooleanType
)

json_schema = StructType([
    StructField("emp_id",     IntegerType(), True),
    StructField("name",       StringType(),  True),
    StructField("department", StringType(),  True),
    StructField("salary",     DoubleType(),  True),
    StructField("age",        IntegerType(), True),
    StructField("join_date",  StringType(),  True),
    StructField("is_active",  BooleanType(), True),
])
df_json_schema = spark.read.schema(json_schema).json(f"{DATA}/employees_flat.json")
df_json_schema.show()

print("\n--- 1C: primitivesAsString - read all values as strings ---")
# Useful when you want to inspect raw values before deciding types.
df_str = spark.read \
    .option("primitivesAsString", "true") \
    .json(f"{DATA}/employees_flat.json")
df_str.show()
df_str.printSchema()


# =============================================================
# SECTION 2 - READ JSON: multi-line array (whole file = one JSON array)
# =============================================================
# When the file is one JSON array spanning multiple lines:
# [
#   {"id": 1, ...},
#   {"id": 2, ...}
# ]
# Set multiLine=True. Without it, the [ ] brackets cause parse errors.

print("\n--- 2: Multi-line JSON array (employees_array.json) ---")
df_array = spark.read \
    .option("multiLine", "true") \
    .json(f"{DATA}/employees_array.json")
df_array.show()
df_array.printSchema()


# =============================================================
# SECTION 3 - READ JSON: nested struct and array fields
# =============================================================
# New imports: col, explode, explode_outer
#
# Spark auto-maps:
#   JSON object  {"city": "..."}  ->  StructType column
#   JSON array   ["a", "b"]       ->  ArrayType column
#
# employees_nested.json has:
#   address: {city, pincode, state}   -> struct
#   skills:  ["Python", "Spark"]      -> array of strings

from pyspark.sql.functions import col, explode, explode_outer

print("\n--- 3A: Nested JSON - raw read, inspect schema ---")
df_nested = spark.read.json(f"{DATA}/employees_nested.json")
df_nested.show(truncate=False)
df_nested.printSchema()

print("\n--- 3B: Dot notation to access struct fields ---")
# col("address.city") drills into the nested struct
df_nested.select(
    col("name"),
    col("address.city").alias("city"),
    col("address.state").alias("state"),
    col("address.pincode").alias("pincode")
).show()

print("\n--- 3C: explode() - one row per array element ---")
# Each skill becomes its own row. Rows with NULL/empty arrays are DROPPED.
df_nested.select(
    col("name"),
    col("department"),
    explode(col("skills")).alias("skill")
).show()

print("\n--- 3D: explode_outer() - keeps NULL/empty array rows ---")
# Same as explode but rows with NULL/empty array get skill = NULL instead of being dropped.
df_nested.select(
    col("name"),
    explode_outer(col("skills")).alias("skill")
).show()


# =============================================================
# SECTION 4 - READ JSON: array of structs (deeply nested)
# =============================================================
# New import: to_json
#
# orders.json has items as an array of structs:
#   items: [{product, qty, price}, {product, qty, price}]
#
# Pattern: explode the array -> each item becomes a struct column
#          then access item.product, item.qty, item.price

from pyspark.sql.functions import to_json

print("\n--- 4A: Orders - array of structs, raw schema ---")
df_orders = spark.read.json(f"{DATA}/orders.json")
df_orders.show(truncate=False)
df_orders.printSchema()

print("\n--- 4B: Flatten - explode items array, then access struct fields ---")
df_flat = df_orders.select(
    col("order_id"),
    col("customer"),
    col("status"),
    explode(col("items")).alias("item")
).select(
    col("order_id"),
    col("customer"),
    col("status"),
    col("item.product").alias("product"),
    col("item.qty").alias("qty"),
    col("item.price").alias("price")
)
df_flat.show()

print("\n--- 4C: to_json() - convert array/struct column back to JSON string ---")
df_orders.select(
    col("order_id"),
    col("customer"),
    to_json(col("items")).alias("items_json_string")
).show(truncate=False)


# =============================================================
# SECTION 5 - PARSE JSON from a STRING column
# =============================================================
# New imports: from_json, get_json_object, json_tuple
#
# Real-world: a table column stores JSON as plain text.
# Three tools to extract fields:
#   from_json()       -> parse full string into a typed struct
#   get_json_object() -> extract one field with JSONPath ($.)
#   json_tuple()      -> extract multiple fields at once

from pyspark.sql.functions import from_json, get_json_object, json_tuple

print("\n--- 5A: from_json() - parse JSON string into a struct ---")
raw_data = [
    (1, '{"city": "Bangalore", "pincode": "560001"}'),
    (2, '{"city": "Mumbai",    "pincode": "400001"}'),
    (3, '{"city": "Hyderabad", "pincode": "500001"}'),
]
df_raw = spark.createDataFrame(raw_data, ["emp_id", "address_json"])

addr_schema = StructType([
    StructField("city",    StringType(), True),
    StructField("pincode", StringType(), True),
])

df_parsed = df_raw.withColumn("address", from_json(col("address_json"), addr_schema))
df_parsed.show()
df_parsed.printSchema()

# Access parsed fields with dot notation
df_parsed.select(
    col("emp_id"),
    col("address.city").alias("city"),
    col("address.pincode").alias("pincode")
).show()

print("\n--- 5B: get_json_object() - one field using JSONPath ---")
# Returns a string column. Best for extracting 1-2 fields quickly.
df_raw.select(
    col("emp_id"),
    get_json_object(col("address_json"), "$.city").alias("city"),
    get_json_object(col("address_json"), "$.pincode").alias("pincode")
).show()

print("\n--- 5C: json_tuple() - multiple fields in one call ---")
# More concise than multiple get_json_object calls.
df_raw.select(
    col("emp_id"),
    json_tuple(col("address_json"), "city", "pincode").alias("city", "pincode")
).show()


# =============================================================
# SECTION 6 - READ TEXT FILE (raw logs)
# =============================================================
# New import: regexp_extract
#
# spark.read.text() reads each line as one row in a column called "value".
# Use regexp_extract() to pull structured fields out using regex.
#
# Log format: "2024-01-15 08:00:01 INFO  UserLogin user_id=101 ..."

from pyspark.sql.functions import regexp_extract

print("\n--- 6A: Read raw text - each line is one row ---")
df_text = spark.read.text(f"{DATA}/logs.txt")
df_text.show(truncate=False)
df_text.printSchema()

print("\n--- 6B: Parse log lines with regexp_extract ---")
# regexp_extract(column, pattern, group_index)
df_logs = df_text.select(
    regexp_extract(col("value"), r"^(\d{4}-\d{2}-\d{2})", 1).alias("log_date"),
    regexp_extract(col("value"), r"^\S+ (\S+)", 1).alias("log_time"),
    regexp_extract(col("value"), r"^\S+ \S+ (\S+)", 1).alias("log_level"),
    regexp_extract(col("value"), r"^\S+ \S+ \S+\s+(\S+)", 1).alias("event"),
    col("value").alias("raw_line")
)
df_logs.show(truncate=False)

print("\n--- 6C: Filter parsed logs ---")
df_logs.filter(col("log_level") == "ERROR").show(truncate=False)

print("\n--- 6D: Count by log level ---")
df_logs.groupBy("log_level").count().orderBy("log_level").show()


# =============================================================
# IMPORTS SUMMARY
# =============================================================
# from pyspark.sql import SparkSession
#
# Section 1: from pyspark.sql.types import
#               StructType, StructField, IntegerType,
#               StringType, DoubleType, BooleanType
#
# Section 3: from pyspark.sql.functions import col, explode, explode_outer
#
# Section 4: from pyspark.sql.functions import to_json
#
# Section 5: from pyspark.sql.functions import from_json, get_json_object, json_tuple
#
# Section 6: from pyspark.sql.functions import regexp_extract

print("\n" + "=" * 60)
print("Day 4 Complete - JSON and Text Reading")
print("=" * 60)

spark.stop()
print("SparkSession stopped. Done.")
