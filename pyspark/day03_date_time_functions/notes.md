# Day 3 — PySpark: Date & Time Functions

> **Roadmap Day:** 3 · **Date:** Wednesday, June 17, 2026  
> **Study Window:** 9 PM – 11 PM  
> **Interview Level:** Easy → Medium

---

## 1. PySpark vs SQL Date Functions — Quick Mapping

| SQL (PostgreSQL) | PySpark | Notes |
|-----------------|---------|-------|
| `ship_date - order_date` | `datediff(end, start)` | PySpark datediff(end_col, start_col) |
| `DATE_TRUNC('month', d)` | `date_trunc('month', col)` | Same name, same units |
| `TO_CHAR(d, 'YYYY-MM')` | `date_format(col, 'yyyy-MM')` | Java datetime format codes |
| `EXTRACT(MONTH FROM d)` | `month(col)` | Also `year()`, `dayofmonth()` |
| `CURRENT_DATE` | `current_date()` | Returns DateType column |
| `order_date + INTERVAL '7 days'` | `date_add(col, 7)` | |
| `order_date - INTERVAL '7 days'` | `date_sub(col, 7)` | |
| `AGE(d1, d2)` in months | `months_between(d1, d2)` | Returns fractional months |
| `date + N months` | `add_months(col, N)` | |

---

## 2. Imports

```python
from pyspark.sql.functions import (
    col, lit,
    datediff, date_trunc, date_format,
    year, month, dayofmonth, dayofweek,
    date_add, date_sub,
    months_between, add_months,
    current_date, to_date,
    min as spark_min, max as spark_max,
    sum as spark_sum, count,
)
from pyspark.sql.types import DateType, DoubleType
```

---

## 3. to_date — Parse Strings to Dates

Always cast string columns to DateType before date arithmetic.

```python
from pyspark.sql.functions import to_date

df = spark.createDataFrame([
    ("2024-01-15",),
    ("2024-03-22",),
], ["order_date_str"])

df = df.withColumn("order_date", to_date("order_date_str", "yyyy-MM-dd"))
df.printSchema()
# root
#  |-- order_date_str: string
#  |-- order_date: date
```

**Java format codes (different from Python strftime!):**

| Code | Meaning | Example |
|------|---------|---------|
| `yyyy` | 4-digit year | 2024 |
| `MM` | 2-digit month | 01..12 |
| `dd` | 2-digit day | 01..31 |
| `HH` | 24-h hour | 00..23 |
| `mm` | minutes | 00..59 |
| `ss` | seconds | 00..59 |

---

## 4. datediff — Days Between Two Dates

```python
from pyspark.sql.functions import datediff, col

# datediff(end_date_col, start_date_col)  →  integer column (days)
df = df.withColumn("delivery_days", datediff(col("ship_date"), col("order_date")))

# Filter slow deliveries
slow = df.filter(col("delivery_days") > 7)
slow.show()
```

**Note:** `datediff(end, start)` — end goes FIRST, start goes second.

---

## 5. date_trunc — Truncate to Calendar Unit

```python
from pyspark.sql.functions import date_trunc

# Truncate to first of month — returns timestamp type
df = df.withColumn("order_month", date_trunc("month", col("order_date")))

# Units: 'year', 'quarter', 'month', 'week', 'day', 'hour', 'minute', 'second'
df.select("order_date", "order_month").show(3)
# +----------+-------------------+
# |order_date|        order_month|
# +----------+-------------------+
# |2024-01-15|2024-01-01 00:00:00|
```

---

## 6. date_format — Format Dates as Strings

```python
from pyspark.sql.functions import date_format

# Java format codes (NOT Python strftime)
df = df.withColumn("ym_label",   date_format(col("order_date"), "yyyy-MM"))
df = df.withColumn("human_date", date_format(col("order_date"), "dd MMM yyyy"))

df.select("order_date", "ym_label", "human_date").show(3)
# +----------+--------+----------+
# |order_date|ym_label|human_date|
# +----------+--------+----------+
# |2024-01-15| 2024-01|15 Jan ...|
```

---

## 7. year / month / dayofmonth — Extract Fields

```python
from pyspark.sql.functions import year, month, dayofmonth, dayofweek

df = df.withColumn("yr",  year(col("order_date")))
df = df.withColumn("mo",  month(col("order_date")))
df = df.withColumn("dy",  dayofmonth(col("order_date")))
df = df.withColumn("dow", dayofweek(col("order_date")))  # 1=Sun, 2=Mon, …

df.select("order_date", "yr", "mo", "dy", "dow").show(3)
```

---

## 8. date_add / date_sub — Add / Subtract Days

```python
from pyspark.sql.functions import date_add, date_sub

# Expected ship date = order_date + 7 days
df = df.withColumn("expected_ship", date_add(col("order_date"), 7))

# 90 days before today
df = df.withColumn("cutoff", date_sub(current_date(), 90))
```

---

## 9. months_between / add_months

```python
from pyspark.sql.functions import months_between, add_months

# Fractional months between two dates
df = df.withColumn("months_active",
                   months_between(col("last_order_date"), col("first_order_date")))

# Add 3 months to a date
df = df.withColumn("renewal_date", add_months(col("order_date"), 3))
```

---

## 10. current_date — Filter Recent Rows

```python
from pyspark.sql.functions import current_date, date_sub

# Filter orders in last 90 days
recent = df.filter(col("order_date") >= date_sub(current_date(), 90))

# Alternative using datediff
recent = df.filter(datediff(current_date(), col("order_date")) <= 90)
```

---

## 11. Day 3 PySpark Problems

### Problem 1 (Easy) — Slow deliveries

```python
from pyspark.sql.functions import datediff, col

df_slow = df_orders.withColumn(
    "delivery_days", datediff(col("ship_date"), col("order_date"))
).filter(
    col("delivery_days") > 7
).orderBy("delivery_days", ascending=False)

df_slow.show()
```

---

### Problem 2 (Easy) — Monthly revenue

```python
from pyspark.sql.functions import date_format, date_trunc, sum as spark_sum, count

df_monthly = (
    df_orders
    .withColumn("month", date_format(col("order_date"), "yyyy-MM"))
    .withColumn("month_ts", date_trunc("month", col("order_date")))   # for ordering
    .groupBy("month_ts", "month")
    .agg(
        spark_sum("amount").alias("total_revenue"),
        count("*").alias("num_orders"),
    )
    .orderBy("month_ts")
    .select("month", "total_revenue", "num_orders")
)

df_monthly.show()
```

---

### Problem 3 (Medium) — New customers

Find customers whose first order was within the last 90 days.

```python
from pyspark.sql.functions import min as spark_min, current_date, date_sub, datediff

df_first_orders = (
    df_orders
    .groupBy("customer_id")
    .agg(spark_min("order_date").alias("first_order_date"))
)

df_new = (
    df_first_orders
    .filter(col("first_order_date") >= date_sub(current_date(), 90))
    .withColumn("days_since_first",
                datediff(current_date(), col("first_order_date")))
    .orderBy("first_order_date", ascending=False)
)

df_new.show()
```

---

## 12. Common Gotchas

| Gotcha | Detail |
|--------|--------|
| `datediff(end, start)` order | End goes FIRST. `datediff(ship_date, order_date)` is correct; reversed gives negative values. |
| Java vs Python format codes | `date_format` uses Java: `yyyy` not `%Y`, `MM` not `%m`. |
| `date_trunc` returns TimestampType | If you need DateType back, wrap with `.cast(DateType())`. |
| `min` name conflict | `from pyspark.sql.functions import min as spark_min` to avoid shadowing Python's built-in `min`. |
| String dates vs DateType | Always use `to_date()` before date arithmetic — string comparison gives wrong results. |

---

## 13. Interview Checklist

| Question | Answer |
|----------|--------|
| `datediff` argument order? | `datediff(end_col, start_col)` — end first. |
| Java vs Python format codes? | PySpark uses Java: `yyyy-MM-dd` not `%Y-%m-%d`. |
| How to get current date in PySpark? | `current_date()` — returns a column expression, not a Python value. |
| `date_trunc` unit strings? | Same as SQL: `'month'`, `'year'`, `'week'`, `'day'`, etc. |
| Monthly grouping in PySpark? | `groupBy(date_format(col, "yyyy-MM"))` or `groupBy(date_trunc("month", col))`. |
| Find new customers (first order in last 90 days)? | `groupBy("customer_id").agg(spark_min("order_date")).filter(col >= date_sub(current_date(), 90))`. |

---

## 14. Quick Reference

```python
# Import once
from pyspark.sql.functions import (
    datediff, date_trunc, date_format,
    year, month, dayofmonth,
    date_add, date_sub,
    months_between, add_months,
    current_date, to_date,
    col, lit,
)

# Parse string to date
to_date(col("col"), "yyyy-MM-dd")

# Days between (end FIRST)
datediff(col("ship_date"), col("order_date"))

# Truncate to month
date_trunc("month", col("order_date"))

# Format as string (Java codes)
date_format(col("order_date"), "yyyy-MM")
date_format(col("order_date"), "dd MMM yyyy")

# Add / subtract days
date_add(col("order_date"), 7)
date_sub(current_date(), 90)

# Extract fields
year(col("d"))   month(col("d"))   dayofmonth(col("d"))

# Months between
months_between(col("end_date"), col("start_date"))

# Current date
current_date()

# Filter last 90 days
df.filter(col("order_date") >= date_sub(current_date(), 90))

# Monthly revenue
df.groupBy(date_format(col("order_date"), "yyyy-MM").alias("month")) \
  .agg(spark_sum("amount").alias("revenue")) \
  .orderBy("month")

# First order date
df.groupBy("customer_id").agg(spark_min("order_date").alias("first_order"))
```
