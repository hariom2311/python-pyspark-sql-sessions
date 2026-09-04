"""
Day 5 - Column Operations and Filtering in PySpark
Topics: Column selection (6 ways), new column creation, type casting,
        filters (single, AND, OR, NOT, isin, between, like, null checks)

Data: 20 e-commerce orders across cities, categories, and statuses.
      Chosen so every filter output is visually distinct from the others.
"""

import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

os.environ['JAVA_HOME']             = 'C:/Program Files/DBeaver/jre'
os.environ['PYSPARK_PYTHON']        = r'C:\Users\hariom\AppData\Local\Programs\Python\Python311\python.exe'
os.environ['PYSPARK_DRIVER_PYTHON'] = r'C:\Users\hariom\AppData\Local\Programs\Python\Python311\python.exe'

from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("Day5 - Column Operations and Filtering") \
    .master("local[*]") \
    .config("spark.sql.shuffle.partitions", "4") \
    .config("spark.ui.showConsoleProgress", "false") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

DATA = "day5-column-filter-operations/data"

print("=" * 60)
print("Day 5 - Column Operations and Filtering")
print("=" * 60)

# ------------------------------------------------------------------
# Load the dataset
# ------------------------------------------------------------------
# 20 e-commerce orders with: customer, city, category, product,
# quantity, unit_price, order_date, status, is_returned

from pyspark.sql.types import (
    StructType, StructField,
    StringType, IntegerType, DoubleType, DateType, BooleanType
)

schema = StructType([
    StructField("order_id",       StringType(),  False),
    StructField("customer_name",  StringType(),  True),
    StructField("city",           StringType(),  True),
    StructField("category",       StringType(),  True),
    StructField("product",        StringType(),  True),
    StructField("quantity",       IntegerType(), True),
    StructField("unit_price",     DoubleType(),  True),
    StructField("order_date",     DateType(),    True),
    StructField("status",         StringType(),  True),
    StructField("is_returned",    BooleanType(), True),
])

df = spark.read \
    .schema(schema) \
    .option("header", "true") \
    .option("dateFormat", "yyyy-MM-dd") \
    .csv(f"{DATA}/orders.csv")

print("\n--- Full Dataset (20 rows) ---")
df.show(20, truncate=False)
df.printSchema()


# =============================================================
# SECTION 1 - COLUMN SELECTION (6 ways)
# =============================================================

from pyspark.sql.functions import col

print("\n" + "=" * 60)
print("SECTION 1 - Column Selection")
print("=" * 60)

# ------ 1A: Select by column name strings ------
# Simplest style. Pass column names as plain strings.
# Use when you just want to pick columns with no transformation.
print("\n--- 1A: String names - pick 3 columns ---")
df.select("order_id", "customer_name", "status").show(5)

# ------ 1B: Select using col() ------
# col() returns a Column object that supports expressions.
# Required whenever you want arithmetic, conditions or aliases.
print("\n--- 1B: col() - same pick but using Column objects ---")
df.select(col("order_id"), col("customer_name"), col("status")).show(5)

# ------ 1C: Select with expression and alias ------
# col() lets you do math inline and rename the result with .alias()
print("\n--- 1C: col() with arithmetic and alias ---")
df.select(
    col("order_id"),
    col("customer_name"),
    col("quantity"),
    col("unit_price"),
    (col("quantity") * col("unit_price")).alias("total_amount")
).show(5)

# ------ 1D: Select using a list variable ------
# Useful when column names come from a variable or are built dynamically.
print("\n--- 1D: List variable - select from a list ---")
cols_needed = ["order_id", "city", "category", "product"]
df.select(cols_needed).show(5)

# ------ 1E: selectExpr - SQL-style expressions as strings ------
# Write SQL expressions directly as strings.
# Great for quick transforms without importing functions.
print("\n--- 1E: selectExpr - SQL expressions as strings ---")
df.selectExpr(
    "order_id",
    "customer_name",
    "quantity * unit_price as total_amount",
    "upper(city) as city_upper"
).show(5)

# ------ 1F: Select all columns + drop unwanted ones ------
# Read all columns first, then drop what you don't need.
# Cleaner than listing 8 out of 10 columns manually.
print("\n--- 1F: Select all then drop specific columns ---")
df.drop("is_returned", "order_date").show(5)


# =============================================================
# SECTION 2 - CREATING NEW COLUMNS (withColumn)
# =============================================================

from pyspark.sql.functions import (
    lit, upper, lower, concat, concat_ws,
    year, month, dayofmonth,
    when, round as spark_round
)

print("\n" + "=" * 60)
print("SECTION 2 - Creating New Columns")
print("=" * 60)

# ------ 2A: Arithmetic - total_amount ------
# The most common new column: multiply two existing columns.
print("\n--- 2A: Arithmetic - quantity * unit_price = total_amount ---")
df.withColumn("total_amount", col("quantity") * col("unit_price")) \
  .select("order_id", "customer_name", "quantity", "unit_price", "total_amount") \
  .show(8)

# ------ 2B: String concat - full label ------
# concat_ws joins strings with a separator.
# Useful for building labels, display names, composite keys.
print("\n--- 2B: String concat - product + city label ---")
df.withColumn("product_city", concat_ws(" | ", col("product"), col("city"))) \
  .select("order_id", "product", "city", "product_city") \
  .show(8)

# ------ 2C: Constant column with lit() ------
# lit() adds the same fixed value to every row.
# Common use: tagging rows with a source system, version, or flag.
print("\n--- 2C: Constant column - tag every row with source system ---")
df.withColumn("source_system", lit("ecommerce_v2")) \
  .withColumn("currency", lit("INR")) \
  .select("order_id", "customer_name", "source_system", "currency") \
  .show(5)

# ------ 2D: Date extraction ------
# year(), month(), dayofmonth() extract parts of a DateType column.
# Enables grouping by month, filtering by year, etc.
print("\n--- 2D: Date extraction - year, month, day from order_date ---")
df.withColumn("order_year",  year(col("order_date"))) \
  .withColumn("order_month", month(col("order_date"))) \
  .withColumn("order_day",   dayofmonth(col("order_date"))) \
  .select("order_id", "order_date", "order_year", "order_month", "order_day") \
  .show(8)

# ------ 2E: Conditional column with when/otherwise ------
# when() = CASE WHEN in SQL. Chain .when() for multiple branches.
# Always end with .otherwise() to handle the remaining rows.
print("\n--- 2E: Conditional - classify order value into tier ---")
df.withColumn("total_amount", col("quantity") * col("unit_price")) \
  .withColumn(
      "order_tier",
      when(col("total_amount") >= 50000, "High Value")
      .when(col("total_amount") >= 10000, "Mid Value")
      .otherwise("Low Value")
  ) \
  .select("order_id", "product", "total_amount", "order_tier") \
  .show(10)

# ------ 2F: Chaining multiple withColumn calls ------
# Each withColumn builds on the previous result.
# The new column from step 1 is available in step 2.
print("\n--- 2F: Chaining - total_amount -> tax -> net_payable ---")
df.withColumn("total_amount", col("quantity") * col("unit_price")) \
  .withColumn("tax",          spark_round(col("total_amount") * 0.18, 2)) \
  .withColumn("net_payable",  spark_round(col("total_amount") + col("tax"), 2)) \
  .select("order_id", "product", "total_amount", "tax", "net_payable") \
  .show(8)


# =============================================================
# SECTION 3 - TYPE CASTING
# =============================================================

print("\n" + "=" * 60)
print("SECTION 3 - Type Casting")
print("=" * 60)

# ------ 3A: Check current types ------
print("\n--- 3A: Current schema - check column types ---")
df.printSchema()

# ------ 3B: Cast using .cast() ------
# .cast("type_name") or .cast(TypeClass()) — both work.
# String type names are simpler to write.
print("\n--- 3B: Cast unit_price (Double) to Integer ---")
df.withColumn("unit_price_int", col("unit_price").cast("int")) \
  .select("order_id", "unit_price", "unit_price_int") \
  .show(5)
# Notice: 75000.0 becomes 75000, decimal part is TRUNCATED (not rounded)

# ------ 3C: Cast Integer to Double ------
print("\n--- 3C: Cast quantity (Integer) to Double ---")
df.withColumn("quantity_dbl", col("quantity").cast("double")) \
  .select("order_id", "quantity", "quantity_dbl") \
  .show(5)

# ------ 3D: Cast to String ------
# Useful for concatenation, logging, or writing to string-typed sinks.
print("\n--- 3D: Cast unit_price (Double) to String ---")
df.withColumn("price_str", col("unit_price").cast("string")) \
  .select("order_id", "unit_price", "price_str") \
  .printSchema()

# ------ 3E: Cast Boolean to Integer (0/1) ------
# Common pattern: true -> 1, false -> 0 for numeric aggregations.
print("\n--- 3E: Cast is_returned (Boolean) to Integer ---")
df.withColumn("returned_flag", col("is_returned").cast("int")) \
  .select("order_id", "is_returned", "returned_flag") \
  .show(8)

# ------ 3F: Wrong cast produces NULL, not an error ------
# If a value cannot be cast, Spark returns NULL (PERMISSIVE behavior).
print("\n--- 3F: Bad cast - casting status (String) to Integer gives NULL ---")
df.withColumn("bad_cast", col("status").cast("int")) \
  .select("order_id", "status", "bad_cast") \
  .show(5)
# Every row in bad_cast is NULL because "delivered"/"shipped" can't be int


# =============================================================
# SECTION 4 - FILTERING
# =============================================================

from pyspark.sql.functions import col

print("\n" + "=" * 60)
print("SECTION 4 - Filtering")
print("=" * 60)

# Before each filter, the full count is 20 rows.
# Watch the row count and values change with each filter.
print(f"\nTotal rows in dataset: {df.count()}")

# ------ 4A: Single condition - equality ------
print("\n--- 4A: Single condition - status == 'delivered' (expect ~13 rows) ---")
df.filter(col("status") == "delivered") \
  .select("order_id", "customer_name", "city", "status") \
  .show(20)

# ------ 4B: Single condition - numeric comparison ------
print("\n--- 4B: Single condition - unit_price > 10000 (expensive items) ---")
df.filter(col("unit_price") > 10000) \
  .select("order_id", "product", "category", "unit_price", "status") \
  .show(20)

# ------ 4C: AND filter (&) ------
# Both conditions MUST be true for a row to pass.
# Use & (not Python 'and'). Wrap each condition in parentheses.
print("\n--- 4C: AND - Electronics AND delivered ---")
print("    (must satisfy BOTH: category=Electronics AND status=delivered)")
df.filter(
    (col("category") == "Electronics") & (col("status") == "delivered")
) \
  .select("order_id", "customer_name", "product", "category", "status") \
  .show(20)
# Compare with 4A (all delivered) and 4D (all Electronics) to see intersection

# ------ 4D: AND filter - different columns ------
print("\n--- 4D: AND - Mumbai city AND unit_price > 5000 ---")
print("    (both conditions must hold: city=Mumbai AND price>5000)")
df.filter(
    (col("city") == "Mumbai") & (col("unit_price") > 5000)
) \
  .select("order_id", "customer_name", "city", "product", "unit_price") \
  .show(20)

# ------ 4E: OR filter (|) ------
# Row passes if EITHER condition is true (or both).
# More rows pass OR than AND.
print("\n--- 4E: OR - cancelled OR is_returned=true ---")
print("    (passes if status=cancelled OR returned — either one is enough)")
df.filter(
    (col("status") == "cancelled") | (col("is_returned") == True)
) \
  .select("order_id", "customer_name", "status", "is_returned") \
  .show(20)

# ------ 4F: OR filter across different columns ------
print("\n--- 4F: OR - Furniture category OR unit_price > 50000 ---")
print("    (big-ticket items by category or by price)")
df.filter(
    (col("category") == "Furniture") | (col("unit_price") > 50000)
) \
  .select("order_id", "product", "category", "unit_price") \
  .show(20)

# ------ 4G: NOT filter (~) ------
# ~ inverts the condition. Every row that failed the inner check now passes.
print("\n--- 4G: NOT - exclude cancelled orders ---")
print("    (~: keep everything that is NOT cancelled)")
df.filter(~(col("status") == "cancelled")) \
  .select("order_id", "customer_name", "status") \
  .show(20)

# ------ 4H: Combining AND + OR + NOT ------
# Use parentheses carefully. AND binds tighter than OR in Spark.
print("\n--- 4H: AND + OR - delivered orders from Electronics OR Furniture ---")
print("    (status=delivered AND (category=Electronics OR category=Furniture))")
df.filter(
    (col("status") == "delivered") &
    ((col("category") == "Electronics") | (col("category") == "Furniture"))
) \
  .select("order_id", "customer_name", "category", "product", "status") \
  .show(20)

# ------ 4I: isin() - match any value in a list ------
# Cleaner alternative to writing many OR conditions.
# isin("a", "b", "c") == (col == "a") | (col == "b") | (col == "c")
print("\n--- 4I: isin - city in [Mumbai, Delhi, Pune] ---")
df.filter(col("city").isin("Mumbai", "Delhi", "Pune")) \
  .select("order_id", "customer_name", "city", "product") \
  .show(20)

# ------ 4J: NOT isin() - exclude a list of values ------
print("\n--- 4J: NOT isin - exclude Electronics and Grocery categories ---")
df.filter(~col("category").isin("Electronics", "Grocery")) \
  .select("order_id", "product", "category", "unit_price") \
  .show(20)

# ------ 4K: between() - numeric range ------
# between(low, high) is INCLUSIVE on both ends.
print("\n--- 4K: between - unit_price between 1000 and 10000 ---")
df.filter(col("unit_price").between(1000, 10000)) \
  .select("order_id", "product", "category", "unit_price") \
  .show(20)

# ------ 4L: like() - string pattern matching ------
# % matches any sequence of characters (like SQL LIKE).
# _ matches exactly one character.
print("\n--- 4L: like - customer_name starts with 'R' ---")
df.filter(col("customer_name").like("R%")) \
  .select("order_id", "customer_name", "city") \
  .show(20)

print("\n--- 4M: like - product contains 'one' anywhere ---")
df.filter(col("product").like("%one%")) \
  .select("order_id", "product", "category") \
  .show(20)

# ------ 4N: isNull / isNotNull ------
# Used when data has missing values.
# Add nulls artificially here to demonstrate.
from pyspark.sql.functions import lit
df_with_nulls = df.withColumn(
    "discount",
    when(col("category") == "Grocery", lit(None).cast("double"))
    .otherwise(col("unit_price") * 0.05)
)

print("\n--- 4N: isNull - rows where discount is NULL (Grocery orders) ---")
df_with_nulls.filter(col("discount").isNull()) \
  .select("order_id", "product", "category", "discount") \
  .show(20)

print("\n--- 4O: isNotNull - rows where discount exists ---")
df_with_nulls.filter(col("discount").isNotNull()) \
  .select("order_id", "product", "category", "discount") \
  .show(10)


# =============================================================
# IMPORTS SUMMARY
# =============================================================
# from pyspark.sql import SparkSession
# from pyspark.sql.types import StructType, StructField, StringType,
#                               IntegerType, DoubleType, DateType, BooleanType
#
# Section 1: from pyspark.sql.functions import col
#
# Section 2: from pyspark.sql.functions import
#               lit, upper, lower, concat_ws,
#               year, month, dayofmonth,
#               when, round
#
# Section 3: col().cast("type")   -- no extra import needed
#
# Section 4: from pyspark.sql.functions import col, lit, when
#            col().isin(...)      -- built into Column, no import
#            col().between(...)   -- built into Column, no import
#            col().like(...)      -- built into Column, no import
#            col().isNull()       -- built into Column, no import

print("\n" + "=" * 60)
print("Day 5 Complete")
print("=" * 60)

spark.stop()
print("SparkSession stopped. Done.")
