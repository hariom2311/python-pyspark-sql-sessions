# Day 6 — PySpark: Window Functions Part 1 (row_number, rank, dense_rank)

> **Roadmap Day:** 6 · **Topics:** Window spec · row_number · rank · dense_rank · filter on window result  
> **Interview Level:** Easy → Medium

---

## 1. PySpark vs SQL Mapping

| SQL | PySpark | Notes |
|-----|---------|-------|
| `PARTITION BY region` | `Window.partitionBy('region')` | Defines the window group |
| `ORDER BY revenue DESC` | `.orderBy(F.desc('revenue'))` | Within-partition ordering |
| `ROW_NUMBER()` | `F.row_number()` | Unique, no ties |
| `RANK()` | `F.rank()` | Gaps after ties |
| `DENSE_RANK()` | `F.dense_rank()` | No gaps after ties |
| CTE filter | `.filter(F.col('drnk') <= 2)` | Filter after `.withColumn()` |

---

## 2. Window Spec

```python
from pyspark.sql import Window
from pyspark.sql import functions as F

# Define a window: partition by region, order by revenue descending
w = Window.partitionBy('region').orderBy(F.desc('revenue'))
```

Reuse `w` across multiple `.withColumn()` calls:
```python
df = df \
    .withColumn('rn',   F.row_number().over(w)) \
    .withColumn('rnk',  F.rank().over(w)) \
    .withColumn('drnk', F.dense_rank().over(w))
```

---

## 3. ROW_NUMBER — Unique Sequential

```python
w = Window.partitionBy('region').orderBy(F.desc('revenue'))

df.withColumn('rn', F.row_number().over(w)).show()
# Within each region: 1, 2, 3, … — no two rows share the same number
# Ties broken arbitrarily (depends on physical order)
```

---

## 4. RANK vs DENSE_RANK

```python
# Both employees with revenue=900 get rank 2 in RANK and DENSE_RANK
# But RANK skips 3 → next is 4; DENSE_RANK does not skip → next is 3

w = Window.partitionBy('region').orderBy(F.desc('revenue'))

df_ranked = (
    df
    .withColumn('rnk',  F.rank().over(w))
    .withColumn('drnk', F.dense_rank().over(w))
)
df_ranked.show()
```

---

## 5. Top-N per Group (Most Common Interview Pattern)

```python
from pyspark.sql import Window
from pyspark.sql import functions as F

w = Window.partitionBy('region').orderBy(F.desc('revenue'))

# Top 2 per region — use dense_rank so ties are both included
df_top2 = (
    df
    .withColumn('drnk', F.dense_rank().over(w))
    .filter(F.col('drnk') <= 2)
)
df_top2.show()
```

---

## 6. Partition by Multiple Columns

```python
# Rank within (region, month) — resets for every region+month combination
w = Window.partitionBy('region', 'month').orderBy(F.desc('revenue'))
```

---

## 7. Day 6 PySpark Solutions

### Problem 1 — Rank employees by revenue within region
```python
from pyspark.sql import Window
from pyspark.sql import functions as F

w = Window.partitionBy('region').orderBy(F.desc('revenue'))

df_p1 = (
    df_sales
    .withColumn('revenue_rank', F.rank().over(w))
    .orderBy('region', 'revenue_rank')
)
df_p1.show()
```

### Problem 2 — Top 2 per region (DENSE_RANK, handle ties)
```python
w = Window.partitionBy('region').orderBy(F.desc('revenue'))

df_p2 = (
    df_sales
    .withColumn('drnk', F.dense_rank().over(w))
    .filter(F.col('drnk') <= 2)
    .orderBy('region', 'drnk')
)
df_p2.show()
```

### Problem 3 — Employees who ranked #1 in any region for any month
```python
# Partition by both region AND month
w = Window.partitionBy('region', 'month').orderBy(F.desc('revenue'))

df_p3 = (
    df_sales
    .withColumn('rnk', F.rank().over(w))
    .filter(F.col('rnk') == 1)
    .select('emp_id', 'region', 'month', 'revenue')
    .distinct()
    .orderBy('region', 'month')
)
df_p3.show()
```

---

## 8. Common Gotchas

| Gotcha | Detail |
|--------|--------|
| No `WHERE` equivalent | You must add the window column with `.withColumn()` first, then `.filter()` |
| `F.desc('col')` not `'col DESC'` | PySpark orderBy inside Window uses `F.desc()`, not a string |
| Window without `PARTITION BY` | `Window.orderBy(...)` alone applies to the ENTIRE DataFrame — usually not what you want |
| `rank()` vs `dense_rank()` for top-N | Use `dense_rank()` — with `rank()`, a tie at rank 1 makes the next person rank 3, which filter `<= 2` might miss or include incorrectly |
| Import | `from pyspark.sql import Window` — separate import from `functions` |

---

## 9. Interview Checklist

- [ ] `Window.partitionBy('col').orderBy(F.desc('val'))` — build the spec first
- [ ] `.withColumn('rn', F.row_number().over(w))` — apply the function
- [ ] `row_number` = unique; `rank` = gaps; `dense_rank` = no gaps
- [ ] Filter AFTER adding the window column — never inside `.agg()`
- [ ] Top-N per group → `dense_rank + filter <= N`
- [ ] Multi-column partition: `Window.partitionBy('a', 'b')`

---

## 10. Quick Reference

```python
from pyspark.sql import Window, functions as F

# Window spec
w = Window.partitionBy('region').orderBy(F.desc('revenue'))

# All three functions
.withColumn('rn',   F.row_number().over(w))   # unique
.withColumn('rnk',  F.rank().over(w))          # gaps on tie
.withColumn('drnk', F.dense_rank().over(w))    # no gaps

# Top-N filter
.filter(F.col('drnk') <= 2)

# Multi-column partition + multi-column sort
w2 = Window.partitionBy('region', 'month').orderBy(F.desc('revenue'), F.asc('emp_id'))
```
