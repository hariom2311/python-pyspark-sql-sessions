"""
Day 6 - GroupBy, Aggregations, Sorting, and Date Functions in PySpark
Topics:
  - groupBy + agg: count, sum, avg, min, max, countDistinct, collect_list
  - orderBy / sort: asc, desc, multiple columns, nulls handling
  - filter after groupBy (HAVING equivalent)
  - Date functions: to_date, current_date, datediff, date_add, date_sub,
                    months_between, last_day, next_day, date_trunc,
                    date_format, dayofweek, dayofyear, quarter, weekofyear

Data: 30 sales records across 5 salespersons, 4 regions, 4 categories,
      6 months (Jan-Jun 2024). Designed so every aggregation gives
      visually distinct output.
"""

import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

os.environ['JAVA_HOME']             = 'C:/Program Files/DBeaver/jre'
os.environ['PYSPARK_PYTHON']        = r'C:\Users\hariom\AppData\Local\Programs\Python\Python311\python.exe'
os.environ['PYSPARK_DRIVER_PYTHON'] = r'C:\Users\hariom\AppData\Local\Programs\Python\Python311\python.exe'

from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("Day6 - GroupBy, Aggregations, Sorting, Date Functions") \
    .master("local[*]") \
    .config("spark.sql.shuffle.partitions", "4") \
    .config("spark.ui.showConsoleProgress", "false") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

DATA = "day6-aggregations-and-window-functions/data"

print("=" * 65)
print("Day 6 - GroupBy, Aggregations, Sorting, Date Functions")
print("=" * 65)

# ------------------------------------------------------------------
# Load dataset
# ------------------------------------------------------------------
# 30 sales: salesperson, region, category, product, quantity,
#           unit_price, sale_date, delivery_date, status

from pyspark.sql.types import (
    StructType, StructField,
    StringType, IntegerType, DoubleType, DateType
)

schema = StructType([
    StructField("sale_id",       StringType(),  False),
    StructField("salesperson",   StringType(),  True),
    StructField("region",        StringType(),  True),
    StructField("category",      StringType(),  True),
    StructField("product",       StringType(),  True),
    StructField("quantity",      IntegerType(), True),
    StructField("unit_price",    DoubleType(),  True),
    StructField("sale_date",     DateType(),    True),
    StructField("delivery_date", DateType(),    True),
    StructField("status",        StringType(),  True),
])

from pyspark.sql.functions import col, round as spark_round

df = spark.read \
    .schema(schema) \
    .option("header", "true") \
    .option("dateFormat", "yyyy-MM-dd") \
    .csv(f"{DATA}/sales.csv")

# Add total_amount column — used throughout all sections
df = df.withColumn("total_amount", spark_round(col("quantity") * col("unit_price"), 2))

print("\n--- Full Dataset (30 rows) ---")
df.show(30, truncate=False)
df.printSchema()


# =============================================================
# SECTION 1 - groupBy + BASIC AGGREGATIONS
# =============================================================
# groupBy(col) groups rows that share the same value.
# agg() applies one or more aggregation functions to each group.
#
# Syntax:
#   df.groupBy("col1", "col2").agg(func("col").alias("name"))
#
# Common functions:
#   count()         - rows in the group
#   sum()           - total of a numeric column
#   avg()           - mean of a numeric column
#   min() / max()   - smallest / largest value
#   countDistinct() - distinct non-null values

from pyspark.sql.functions import (
    count, sum as spark_sum, avg, min as spark_min,
    max as spark_max, countDistinct, collect_list, collect_set
)

print("\n" + "=" * 65)
print("SECTION 1 - groupBy + Basic Aggregations")
print("=" * 65)

# ------ 1A: count() - how many sales per category ------
# count("*") counts all rows including nulls.
# count("col") counts non-null values in that column only.
print("\n--- 1A: count - number of sales per category ---")
df.groupBy("category") \
  .agg(count("*").alias("total_sales")) \
  .show()
# Electronics=7, Clothing=7, Grocery=7, Furniture=6 -> visually distinct

# ------ 1B: sum() - total revenue per region ------
print("\n--- 1B: sum - total revenue per region ---")
df.groupBy("region") \
  .agg(spark_sum("total_amount").alias("total_revenue")) \
  .show()

# ------ 1C: avg() - average sale value per salesperson ------
print("\n--- 1C: avg - average sale amount per salesperson ---")
df.groupBy("salesperson") \
  .agg(spark_round(avg("total_amount"), 2).alias("avg_sale_amount")) \
  .show()

# ------ 1D: min() and max() - price range per category ------
print("\n--- 1D: min & max - cheapest and most expensive unit price per category ---")
df.groupBy("category") \
  .agg(
      spark_min("unit_price").alias("min_price"),
      spark_max("unit_price").alias("max_price")
  ) \
  .show()

# ------ 1E: Multiple aggregations in one call ------
# Pass multiple functions inside a single agg().
# This is efficient — Spark computes all in one pass over the data.
print("\n--- 1E: Multiple agg - full summary per category ---")
df.groupBy("category") \
  .agg(
      count("*").alias("num_sales"),
      spark_sum("total_amount").alias("total_revenue"),
      spark_round(avg("total_amount"), 2).alias("avg_revenue"),
      spark_min("unit_price").alias("min_price"),
      spark_max("unit_price").alias("max_price")
  ) \
  .show()

# ------ 1F: countDistinct() - unique products per region ------
# Different from count() — only counts distinct non-null values.
print("\n--- 1F: countDistinct - unique products sold per region ---")
df.groupBy("region") \
  .agg(countDistinct("product").alias("unique_products")) \
  .show()

# ------ 1G: groupBy multiple columns ------
# Group by more than one column — produces finer-grained buckets.
print("\n--- 1G: groupBy 2 columns - sales count by region + category ---")
df.groupBy("region", "category") \
  .agg(
      count("*").alias("num_sales"),
      spark_sum("total_amount").alias("total_revenue")
  ) \
  .show(20)

# ------ 1H: collect_list vs collect_set ------
# collect_list - all values in the group as an array (duplicates kept)
# collect_set  - unique values only (order not guaranteed)
print("\n--- 1H: collect_list - all products sold by each salesperson ---")
df.groupBy("salesperson") \
  .agg(collect_list("product").alias("products_sold")) \
  .show(truncate=False)

print("\n--- 1H: collect_set - unique categories sold by each salesperson ---")
df.groupBy("salesperson") \
  .agg(collect_set("category").alias("categories")) \
  .show(truncate=False)


# =============================================================
# SECTION 2 - FILTER AFTER groupBy (HAVING equivalent)
# =============================================================
# SQL has HAVING to filter on aggregated values.
# In PySpark: groupBy().agg().filter() — chain a filter AFTER agg().
#
# Key rule: you CANNOT filter on the aggregated alias directly in the
# same agg() call. You must chain .filter() after .agg().

print("\n" + "=" * 65)
print("SECTION 2 - Filter After groupBy (HAVING equivalent)")
print("=" * 65)

# ------ 2A: Regions with total revenue > 1,00,000 ------
print("\n--- 2A: HAVING - regions with total_revenue > 100000 ---")
df.groupBy("region") \
  .agg(spark_sum("total_amount").alias("total_revenue")) \
  .filter(col("total_revenue") > 100000) \
  .show()

# ------ 2B: Salespersons with more than 5 sales ------
print("\n--- 2B: HAVING - salespersons with more than 5 sales ---")
df.groupBy("salesperson") \
  .agg(count("*").alias("num_sales")) \
  .filter(col("num_sales") > 5) \
  .show()

# ------ 2C: Categories where avg unit_price > 5000 ------
print("\n--- 2C: HAVING - categories where avg unit_price > 5000 ---")
df.groupBy("category") \
  .agg(spark_round(avg("unit_price"), 2).alias("avg_price")) \
  .filter(col("avg_price") > 5000) \
  .show()


# =============================================================
# SECTION 3 - orderBy / sort
# =============================================================
# orderBy() and sort() are identical — use either.
# Default direction is ASCENDING.
#
# Two ways to set direction:
#   col("x").asc()  / col("x").desc()
#   asc("x")        / desc("x")         -- from pyspark.sql.functions

from pyspark.sql.functions import asc, desc

print("\n" + "=" * 65)
print("SECTION 3 - orderBy / sort")
print("=" * 65)

# ------ 3A: Single column ascending (default) ------
print("\n--- 3A: Sort by total_amount ascending (cheapest first) ---")
df.select("sale_id", "salesperson", "product", "total_amount") \
  .orderBy("total_amount") \
  .show(10)

# ------ 3B: Single column descending ------
print("\n--- 3B: Sort by total_amount descending (most expensive first) ---")
df.select("sale_id", "salesperson", "product", "total_amount") \
  .orderBy(col("total_amount").desc()) \
  .show(10)

# ------ 3C: Multiple columns ------
# Primary sort: region A-Z. Within each region, secondary sort: total_amount desc.
print("\n--- 3C: Sort by region asc, then total_amount desc ---")
df.select("sale_id", "salesperson", "region", "product", "total_amount") \
  .orderBy(col("region").asc(), col("total_amount").desc()) \
  .show(15)

# ------ 3D: Sort aggregated results ------
# Very common pattern: group -> aggregate -> sort results
print("\n--- 3D: Top salespersons by total revenue (aggregated + sorted) ---")
df.groupBy("salesperson") \
  .agg(
      count("*").alias("num_sales"),
      spark_round(spark_sum("total_amount"), 2).alias("total_revenue")
  ) \
  .orderBy(col("total_revenue").desc()) \
  .show()

# ------ 3E: Sort by multiple aggregated columns ------
print("\n--- 3E: Category summary sorted by num_sales desc, then total_revenue desc ---")
df.groupBy("category") \
  .agg(
      count("*").alias("num_sales"),
      spark_round(spark_sum("total_amount"), 2).alias("total_revenue")
  ) \
  .orderBy(col("num_sales").desc(), col("total_revenue").desc()) \
  .show()

# ------ 3F: asc_nulls_first / desc_nulls_last ------
# By default, NULLs sort last in ASC and first in DESC.
# Override with asc_nulls_first(), asc_nulls_last(), desc_nulls_first(), desc_nulls_last()
print("\n--- 3F: Null handling in sort - desc_nulls_last ---")
from pyspark.sql.functions import when, lit
df_with_nulls = df.withColumn(
    "discount",
    when(col("category") == "Grocery", lit(None).cast("double"))
    .otherwise(col("total_amount") * 0.10)
)
df_with_nulls.select("sale_id", "category", "total_amount", "discount") \
  .orderBy(col("discount").desc_nulls_last()) \
  .show(10)


# =============================================================
# SECTION 4 - DATE FUNCTIONS (complete coverage)
# =============================================================
# Day 5 covered: year(), month(), dayofmonth()
# This section covers ALL remaining date functions.
#
# Reference columns: sale_date, delivery_date (both DateType)

from pyspark.sql.functions import (
    current_date,
    datediff,
    date_add,
    date_sub,
    months_between,
    last_day,
    next_day,
    date_trunc,
    date_format,
    dayofweek,
    dayofyear,
    quarter,
    weekofyear,
    to_date,
    trunc,
)

print("\n" + "=" * 65)
print("SECTION 4 - Date Functions")
print("=" * 65)

# ------ 4A: current_date() ------
# Returns today's date (server date at query execution time).
# Useful for calculating age of records, days since event, etc.
print("\n--- 4A: current_date - today's date ---")
df.select(
    "sale_id",
    "sale_date",
    current_date().alias("today")
).show(5)

# ------ 4B: datediff() ------
# datediff(end, start) -> number of days between two dates.
# Result is positive when end > start.
# Two uses: delivery time (delivery_date - sale_date), days since sale (today - sale_date)
print("\n--- 4B: datediff - delivery days and days since sale ---")
df.select(
    "sale_id",
    "sale_date",
    "delivery_date",
    datediff(col("delivery_date"), col("sale_date")).alias("delivery_days"),
    datediff(current_date(), col("sale_date")).alias("days_since_sale")
).show(10)

# ------ 4C: date_add() and date_sub() ------
# date_add(date, n)  -> add n days to the date
# date_sub(date, n)  -> subtract n days from the date
# Common use: calculate SLA deadline, look-back windows
print("\n--- 4C: date_add & date_sub - SLA deadline and look-back ---")
df.select(
    "sale_id",
    "sale_date",
    date_add(col("sale_date"), 7).alias("sla_deadline_7d"),
    date_sub(col("sale_date"), 3).alias("three_days_before"),
).show(8)

# ------ 4D: months_between() ------
# Returns fractional months between two dates.
# Use round() to get whole months.
print("\n--- 4D: months_between - months since sale ---")
df.select(
    "sale_id",
    "sale_date",
    spark_round(months_between(current_date(), col("sale_date")), 1).alias("months_since_sale")
).show(8)

# ------ 4E: last_day() ------
# Returns the last day of the month for a given date.
# Useful for month-end reporting, billing cycles.
print("\n--- 4E: last_day - last day of sale month ---")
df.select(
    "sale_id",
    "sale_date",
    last_day(col("sale_date")).alias("month_end")
).show(8)

# ------ 4F: next_day() ------
# Returns the next occurrence of a given weekday after the date.
# Weekday names: "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"
print("\n--- 4F: next_day - next Monday after sale_date ---")
df.select(
    "sale_id",
    "sale_date",
    next_day(col("sale_date"), "Mon").alias("next_monday")
).show(8)

# ------ 4G: date_trunc() ------
# Truncates a date/timestamp to the start of the given unit.
# Units: "year", "month", "week", "day", "hour", "minute", "second"
# Very common for grouping by month or year in reports.
print("\n--- 4G: date_trunc - truncate to month start (for monthly grouping) ---")
df.select(
    "sale_id",
    "sale_date",
    date_trunc("month", col("sale_date")).alias("month_start"),
    date_trunc("year",  col("sale_date")).alias("year_start")
).show(8)

# ------ 4H: date_format() ------
# Formats a date into a string using Java date format patterns.
# Common patterns:
#   yyyy  = 4-digit year     MM   = 2-digit month    dd = 2-digit day
#   MMM   = month name abbr  MMMM = full month name  EEE = weekday abbr
print("\n--- 4H: date_format - custom display formats ---")
df.select(
    "sale_id",
    "sale_date",
    date_format(col("sale_date"), "dd-MM-yyyy").alias("indian_format"),
    date_format(col("sale_date"), "MMM yyyy").alias("month_year"),
    date_format(col("sale_date"), "EEEE").alias("weekday_name"),
    date_format(col("sale_date"), "MM/dd/yyyy").alias("us_format")
).show(8)

# ------ 4I: dayofweek() ------
# Returns day of week as integer: 1=Sunday, 2=Monday, ..., 7=Saturday
# (Spark follows Java convention: week starts on Sunday)
print("\n--- 4I: dayofweek - day number (1=Sun, 2=Mon, ..., 7=Sat) ---")
df.select(
    "sale_id",
    "sale_date",
    dayofweek(col("sale_date")).alias("day_of_week_num"),
    date_format(col("sale_date"), "EEE").alias("day_name")
).show(8)

# ------ 4J: dayofyear() ------
# Returns the day number within the year (1-365/366).
print("\n--- 4J: dayofyear - which day of the year ---")
df.select(
    "sale_id",
    "sale_date",
    dayofyear(col("sale_date")).alias("day_of_year")
).show(8)

# ------ 4K: quarter() ------
# Returns the quarter (1, 2, 3, or 4) for a date.
# Q1=Jan-Mar, Q2=Apr-Jun, Q3=Jul-Sep, Q4=Oct-Dec
print("\n--- 4K: quarter - which quarter ---")
df.select(
    "sale_id",
    "sale_date",
    quarter(col("sale_date")).alias("quarter")
).show(8)

print("\n--- 4K: sales count and revenue by quarter ---")
df.groupBy(quarter(col("sale_date")).alias("quarter")) \
  .agg(
      count("*").alias("num_sales"),
      spark_round(spark_sum("total_amount"), 2).alias("total_revenue")
  ) \
  .orderBy("quarter") \
  .show()

# ------ 4L: weekofyear() ------
# Returns the ISO week number of the year (1-53).
print("\n--- 4L: weekofyear - ISO week number ---")
df.select(
    "sale_id",
    "sale_date",
    weekofyear(col("sale_date")).alias("week_of_year")
).show(8)

# ------ 4M: to_date() - parse string to DateType ------
# When data arrives as string columns, use to_date() to convert.
# Provide the format pattern that matches your string.
print("\n--- 4M: to_date - parse date strings into DateType ---")
raw_dates = spark.createDataFrame([
    (1, "05-01-2024"),
    (2, "12-01-2024"),
    (3, "20/02/2024"),
], ["id", "date_str"])

raw_dates.select(
    "id",
    "date_str",
    to_date(col("date_str"), "dd-MM-yyyy").alias("parsed_date_1"),
    to_date(col("date_str"), "dd/MM/yyyy").alias("parsed_date_2"),
).show()
# Row 3 with "/" will parse correctly with the second format pattern

# ------ 4N: trunc() - truncate to year or month (older API) ------
# trunc(date, "year") -> first day of year  (2024-01-01)
# trunc(date, "month") -> first day of month (2024-03-01)
# Similar to date_trunc but older, only supports year/month/week.
print("\n--- 4N: trunc - truncate to year / month ---")
df.select(
    "sale_id",
    "sale_date",
    trunc(col("sale_date"), "month").alias("first_of_month"),
    trunc(col("sale_date"), "year").alias("first_of_year")
).show(8)

# ------ 4O: Combine date functions with groupBy ------
# Practical pattern: extract month -> group by it -> aggregate.
# This is how monthly/quarterly reports are built.
print("\n--- 4O: Monthly revenue report using date_format + groupBy ---")
from pyspark.sql.functions import year, month

df.groupBy(
    year(col("sale_date")).alias("year"),
    month(col("sale_date")).alias("month"),
    date_format(col("sale_date"), "MMM yyyy").alias("month_label")
) \
  .agg(
      count("*").alias("num_sales"),
      spark_round(spark_sum("total_amount"), 2).alias("total_revenue")
  ) \
  .orderBy("year", "month") \
  .show()

# ------ 4P: datediff-based analysis ------
# Real-world: flag slow deliveries (took more than 7 days)
print("\n--- 4P: Flag slow deliveries (delivery_days > 7) ---")
df.withColumn("delivery_days", datediff(col("delivery_date"), col("sale_date"))) \
  .withColumn(
      "delivery_speed",
      when(col("delivery_days") <= 3, "Fast")
      .when(col("delivery_days") <= 7, "Normal")
      .otherwise("Slow")
  ) \
  .select("sale_id", "salesperson", "product", "sale_date", "delivery_date",
          "delivery_days", "delivery_speed") \
  .orderBy(col("delivery_days").desc()) \
  .show(15)


# =============================================================
# IMPORTS SUMMARY
# =============================================================
# from pyspark.sql import SparkSession
# from pyspark.sql.types import StructType, StructField, StringType,
#                               IntegerType, DoubleType, DateType
#
# Section 1: from pyspark.sql.functions import
#               count, sum, avg, min, max, countDistinct,
#               collect_list, collect_set, col, round
#
# Section 2: filter() after agg() -- no new imports
#
# Section 3: from pyspark.sql.functions import asc, desc
#            col().asc(), col().desc(), col().desc_nulls_last()
#
# Section 4 - Date functions:
#   current_date     - today's date
#   datediff         - days between two dates
#   date_add         - add N days
#   date_sub         - subtract N days
#   months_between   - fractional months between dates
#   last_day         - last day of month
#   next_day         - next occurrence of weekday
#   date_trunc       - truncate to start of unit (month/year/week)
#   date_format      - format date as string (display)
#   dayofweek        - 1=Sun ... 7=Sat
#   dayofyear        - 1-365
#   quarter          - 1-4
#   weekofyear       - ISO week 1-53
#   to_date          - parse string -> DateType
#   trunc            - truncate to month/year (older API)
#   year, month, dayofmonth -- covered in Day 5

print("\n" + "=" * 65)
print("Day 6 Complete - GroupBy, Aggregations, Sorting, Date Functions")
print("=" * 65)

spark.stop()
print("SparkSession stopped. Done.")
