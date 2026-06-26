# Day 5 — PySpark: All Joins

> **Roadmap Day:** 5 · **Date:** Friday, June 19, 2026  
> **Study Window:** 9 PM – 11 PM  
> **Interview Level:** Easy → Medium

---

## 1. PySpark vs SQL Join Mapping

| SQL | PySpark | Notes |
|-----|---------|-------|
| `INNER JOIN` | `df1.join(df2, on, how='inner')` | Default — `how` can be omitted |
| `LEFT JOIN` | `df1.join(df2, on, how='left')` | also `'left_outer'` |
| `RIGHT JOIN` | `df1.join(df2, on, how='right')` | also `'right_outer'` |
| `FULL OUTER JOIN` | `df1.join(df2, on, how='outer')` | also `'full'` or `'full_outer'` |
| `CROSS JOIN` | `df1.crossJoin(df2)` | No `on` condition — all rows × all rows |
| `SELF JOIN` | `df.alias('e').join(df.alias('m'), ...)` | Same DataFrame aliased twice |

---

## 2. Imports & Spark Setup

```python
import os
os.environ['JAVA_HOME']             = 'C:/Program Files/DBeaver/jre'
os.environ['PYSPARK_PYTHON']        = r'C:\Users\hariom\AppData\Local\Programs\Python\Python311\python.exe'
os.environ['PYSPARK_DRIVER_PYTHON'] = r'C:\Users\hariom\AppData\Local\Programs\Python\Python311\python.exe'

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import *

spark = SparkSession.builder \
    .master('local[*]') \
    .appName('Day5_Joins') \
    .getOrCreate()
spark.sparkContext.setLogLevel('ERROR')
```

---

## 3. INNER JOIN

Returns only rows that match on **both** sides.

```python
df_result = df_orders.join(df_customers, on='customer_id', how='inner')

# Multiple join keys
df_result = df_a.join(df_b, on=['key1', 'key2'], how='inner')

# Custom condition (when column names differ)
df_result = df_orders.join(
    df_customers,
    df_orders.cust_id == df_customers.customer_id,
    how='inner'
)
```

**Key point:** When `on` is a string or list, the join key column appears **once** in the result.  
When `on` is a Column expression, both columns appear — select carefully.

---

## 4. LEFT JOIN

All rows from the left DataFrame; NULL for unmatched right rows.

```python
df_result = df_customers.join(df_orders, on='customer_id', how='left')

# Find customers with NO orders — LEFT + filter NULL
df_no_orders = (
    df_customers
    .join(df_orders, on='customer_id', how='left')
    .filter(F.col('order_id').isNull())
    .select('customer_id', 'name', 'email')
)
```

**Note:** Use `.isNull()` not `== None` — `== None` does not work correctly in PySpark.

---

## 5. RIGHT JOIN

All rows from the right DataFrame; NULL for unmatched left rows.

```python
df_result = df_customers.join(df_orders, on='customer_id', how='right')
# Equivalent: df_orders.join(df_customers, on='customer_id', how='left')
```

---

## 6. FULL OUTER JOIN

All rows from both sides; NULL where there is no match.

```python
df_result = df_customers.join(df_orders, on='customer_id', how='outer')

# Only unmatched rows from EITHER side
df_unmatched = (
    df_customers.join(df_orders, on='customer_id', how='outer')
    .filter(
        F.col('order_id').isNull() | F.col('name').isNull()
    )
)
```

---

## 7. SELF JOIN

Join a DataFrame to **itself** — use `.alias()` to create two references.

```python
# employees: emp_id, name, role, manager_id
emp = df_employees.alias('e')
mgr = df_employees.alias('m')

df_result = (
    emp.join(
        mgr,
        F.col('e.manager_id') == F.col('m.emp_id'),
        how='left'           # LEFT so CEO (NULL manager_id) still appears
    )
    .select(
        F.col('e.emp_id'),
        F.col('e.name').alias('employee'),
        F.col('e.role'),
        F.col('m.name').alias('manager'),
    )
    .orderBy('e.emp_id')
)
```

**Critical:** With self joins you **must** use `F.col('alias.column')` syntax — not `df.column` — because both sides are the same object.

---

## 8. CROSS JOIN

Cartesian product — every row paired with every other row.  
Result rows = left_count × right_count.

```python
df_result = df_customers.crossJoin(df_products)
# 5 customers × 4 products = 20 rows
```

No `on` condition. Use intentionally — a large cross join will OOM your driver.

---

## 9. LEFT JOIN + GROUP BY (most common DE pattern)

Total revenue per customer, including customers with zero orders:

```python
df_result = (
    df_customers
    .join(df_orders, on='customer_id', how='left')
    .groupBy('customer_id', 'name')
    .agg(
        F.count('order_id').alias('total_orders'),        # count non-NULL order_id
        F.coalesce(F.sum('amount'), F.lit(0)).alias('total_revenue'),
    )
    .orderBy('total_revenue', ascending=False)
)
```

**Pattern:** `F.coalesce(F.sum('amount'), F.lit(0))` — returns 0 instead of NULL when no orders exist.

---

## 10. Handling Ambiguous Column Names

When both DataFrames have a column with the same name (other than the join key):

```python
# Problem: both have 'status' column
df_result = df_orders.join(df_customers, on='customer_id', how='inner')
df_result.select('status')   # AnalysisException: ambiguous column 'status'

# Fix 1: rename before join
df_orders_renamed = df_orders.withColumnRenamed('status', 'order_status')

# Fix 2: select with DataFrame prefix after join
df_result = df_orders.alias('o').join(df_customers.alias('c'), ...)
df_result.select(F.col('o.status'), F.col('c.status'))

# Fix 3: drop the duplicate column after join
df_result = df_orders.join(df_customers, on='customer_id').drop(df_customers.status)
```

---

## 11. Day 5 PySpark Solutions

### Problem 1 (Easy) — INNER JOIN orders + customers
```python
df_inner = (
    df_orders
    .join(df_customers, on='customer_id', how='inner')
    .select('order_id', 'name', 'city', 'amount', 'status')
    .orderBy('order_id')
)
df_inner.show()
```

### Problem 2 (Easy) — LEFT JOIN + isNull: customers with no orders
```python
df_no_orders = (
    df_customers
    .join(df_orders, on='customer_id', how='left')
    .filter(F.col('order_id').isNull())
    .select('customer_id', 'name', 'email')
)
df_no_orders.show()
```

### Problem 3 (Medium) — LEFT JOIN + GROUP BY: revenue per customer
```python
df_revenue = (
    df_customers
    .join(df_orders, on='customer_id', how='left')
    .groupBy('customer_id', 'name')
    .agg(
        F.count('order_id').alias('total_orders'),
        F.coalesce(F.sum('amount'), F.lit(0)).alias('total_revenue'),
    )
    .orderBy('total_revenue', ascending=False)
)
df_revenue.show()
```

### Problem 4 (Easy) — SELF JOIN: employee → manager
```python
emp = df_employees.alias('e')
mgr = df_employees.alias('m')

df_hierarchy = (
    emp.join(
        mgr,
        F.col('e.manager_id') == F.col('m.emp_id'),
        how='left'
    )
    .select(
        F.col('e.emp_id'),
        F.col('e.name').alias('employee'),
        F.col('e.role'),
        F.col('m.name').alias('manager'),
    )
    .orderBy('e.emp_id')
)
df_hierarchy.show()
```

### Problem 5 (Medium) — FULL OUTER JOIN: unmatched rows on both sides
```python
df_full = (
    df_customers
    .join(df_orders, on='customer_id', how='outer')
    .filter(
        F.col('order_id').isNull() | F.col('name').isNull()
    )
    .select(
        F.col('name').alias('customer'),
        'order_id',
        'amount',
        F.when(F.col('name').isNull(), 'Orphan order')
         .otherwise('No orders')
         .alias('reason')
    )
)
df_full.show()
```

### Problem 6 (Easy) — CROSS JOIN: all combinations
```python
df_catalog = (
    df_customers
    .crossJoin(df_products)
    .select(
        F.col('name').alias('customer'),
        'product_name',
        'category',
        'price',
    )
    .orderBy('name', 'product_name')
)
print('Total rows:', df_catalog.count())   # 5 × 4 = 20
df_catalog.show()
```

---

## 12. Common Gotchas

| Gotcha | Detail |
|--------|--------|
| `== None` doesn't work | Use `.isNull()` / `.isNotNull()` for NULL checks |
| Ambiguous column name | Prefix with alias: `F.col('e.name')` after aliasing |
| CROSS JOIN on big data | Can produce billions of rows — always check sizes first |
| `how='outer'` variants | `'outer'`, `'full'`, `'full_outer'` all work |
| Self join without alias | Will fail — must call `.alias()` before referencing columns |
| String `on` vs Column `on` | String/list `on` deduplicates the key; Column `on` keeps both copies |

---

## 13. Interview Checklist

- [ ] Write an INNER JOIN — include only matched rows
- [ ] LEFT JOIN + `isNull()` to find "no match" rows
- [ ] LEFT JOIN + `groupBy` + `coalesce(sum, lit(0))` for zero-order customers
- [ ] SELF JOIN — alias the same DataFrame twice with `.alias()`
- [ ] FULL OUTER JOIN — detect mismatches on both sides
- [ ] CROSS JOIN — `crossJoin()`, no condition
- [ ] Handle ambiguous column names after a join

---

## 14. Quick Reference

```python
# INNER
df1.join(df2, on='key', how='inner')

# LEFT (find no-match)
df1.join(df2, on='key', how='left').filter(F.col('df2_col').isNull())

# RIGHT
df1.join(df2, on='key', how='right')

# FULL OUTER
df1.join(df2, on='key', how='outer')

# SELF — must alias
a = df.alias('a'); b = df.alias('b')
a.join(b, F.col('a.mgr_id') == F.col('b.id'), how='left')

# CROSS
df1.crossJoin(df2)

# LEFT + GROUP BY + coalesce
df1.join(df2, on='key', how='left') \
   .groupBy('id', 'name') \
   .agg(F.count('order_id').alias('orders'),
        F.coalesce(F.sum('amount'), F.lit(0)).alias('revenue'))
```
