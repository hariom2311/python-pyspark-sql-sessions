# Day 6 — PySpark: Multi-level Grouping (groupBy, rollup, cube)

> **Roadmap Day:** 6 · **Date:** Saturday, June 21, 2026  
> **Study Window:** 9 PM – 11 PM  
> **Interview Level:** Easy → Medium

---

## 1. PySpark vs SQL Mapping

| SQL | PySpark | Result |
|-----|---------|--------|
| `GROUP BY a, b` | `.groupBy('a','b').agg(...)` | One row per (a, b) |
| `GROUP BY ROLLUP(a, b)` | `.rollup('a','b').agg(...)` | (a,b) + (a) + grand total |
| `GROUP BY CUBE(a, b)` | `.cube('a','b').agg(...)` | All 4 combinations |
| `GROUPING(col)` | `F.grouping('col')` | 1 = rolled up, 0 = real value |
| `COALESCE(col, 'ALL')` | `F.coalesce(F.col('col'), F.lit('ALL'))` | Label NULL rows |

---

## 2. Basic groupBy (recap)

```python
df.groupBy('region', 'category') \
  .agg(F.sum('revenue').alias('total_revenue')) \
  .orderBy('region', 'category') \
  .show()
```

---

## 3. rollup — Hierarchical Subtotals

```python
df.rollup('region', 'category') \
  .agg(F.sum('revenue').alias('total_revenue')) \
  .orderBy('region', 'category') \
  .show()
# NULL region + NULL category = grand total
# NULL category with real region = region subtotal
```

**Label the NULL rows with `coalesce`:**
```python
from pyspark.sql import functions as F

(
    df.rollup('region', 'category')
    .agg(F.sum('revenue').alias('total_revenue'))
    .withColumn('region',   F.coalesce(F.col('region'),   F.lit('ALL REGIONS')))
    .withColumn('category', F.coalesce(F.col('category'), F.lit('ALL CATEGORIES')))
    .orderBy('region', 'category')
    .show()
)
```

**Detect rollup level with `F.grouping()`:**
```python
(
    df.rollup('region', 'category')
    .agg(
        F.sum('revenue').alias('total_revenue'),
        F.grouping('region').alias('region_rolled'),
        F.grouping('category').alias('cat_rolled'),
    )
    .show()
)
# region_rolled=1 means that row's region is a subtotal
```

---

## 4. cube — All Combinations

```python
df.cube('region', 'category') \
  .agg(F.sum('revenue').alias('total_revenue')) \
  .orderBy('region', 'category') \
  .show()
# Produces: (region,category), (region), (category), ()
# ROLLUP only gives: (region,category), (region), ()
# CUBE adds the (category) subtotal that ROLLUP omits
```

---

## 5. Day 6 PySpark Solutions

### Problem 1 (Easy) — Total revenue by region and category
```python
df_p1 = (
    df_sales
    .groupBy('region', 'category')
    .agg(F.round(F.sum('revenue'), 2).alias('total_revenue'))
    .orderBy('region', 'category')
)
df_p1.show()
```

### Problem 2 (Medium) — ROLLUP: region → category → grand total
```python
df_p2 = (
    df_sales
    .rollup('region', 'category')
    .agg(F.round(F.sum('revenue'), 2).alias('total_revenue'))
    .withColumn('region',   F.coalesce(F.col('region'),   F.lit('ALL REGIONS')))
    .withColumn('category', F.coalesce(F.col('category'), F.lit('ALL CATEGORIES')))
    .orderBy('region', 'category')
)
df_p2.show()
```

### Problem 3 (Medium) — CUBE: (region), (category), (region+category)
```python
df_p3 = (
    df_sales
    .cube('region', 'category')
    .agg(
        F.round(F.sum('revenue'), 2).alias('total_revenue'),
        F.grouping('region').alias('region_rolled'),
        F.grouping('category').alias('cat_rolled'),
    )
    .withColumn('region',   F.coalesce(F.col('region'),   F.lit('ALL')))
    .withColumn('category', F.coalesce(F.col('category'), F.lit('ALL')))
    .withColumn('grouping_level',
        F.when((F.col('region_rolled') == 0) & (F.col('cat_rolled') == 0), 'region+category')
         .when((F.col('region_rolled') == 0) & (F.col('cat_rolled') == 1), 'region only')
         .when((F.col('region_rolled') == 1) & (F.col('cat_rolled') == 0), 'category only')
         .otherwise('grand total')
    )
    .drop('region_rolled', 'cat_rolled')
    .orderBy('grouping_level', 'region', 'category')
)
df_p3.show()
```

---

## 6. Common Gotchas

| Gotcha | Detail |
|--------|--------|
| NULL = rolled up | In rollup/cube output, NULL means that column was aggregated away — not missing data |
| `coalesce` order | `F.coalesce(F.col('region'), F.lit('ALL'))` — col first, literal fallback second |
| ROLLUP vs CUBE | ROLLUP is hierarchical (region→category→total); CUBE adds cross-dimension subtotals |
| `F.grouping('col')` | Returns 1 if that column was rolled up in that row, 0 if it's a real value |
| Chain `.agg()` | You can mix regular aggs + `F.grouping()` in the same `.agg()` call |

---

## 7. Interview Checklist

- [ ] `.groupBy().agg()` — multi-column grouping
- [ ] `.rollup()` — hierarchical subtotals, understand the NULL meaning
- [ ] `.cube()` — all combinations including cross-dimension subtotals
- [ ] `F.coalesce(col, lit('ALL'))` — label rollup NULL rows
- [ ] `F.grouping('col')` — detect which level a row represents
- [ ] Difference between ROLLUP and CUBE output

---

## 8. Quick Reference

```python
# Basic groupBy
df.groupBy('a', 'b').agg(F.sum('val').alias('total'))

# ROLLUP — hierarchical
df.rollup('a', 'b').agg(F.sum('val').alias('total'))

# CUBE — all combinations
df.cube('a', 'b').agg(F.sum('val').alias('total'))

# Label NULLs
.withColumn('a', F.coalesce(F.col('a'), F.lit('ALL')))

# Detect rollup level
F.grouping('col')    # 1 = rolled up, 0 = real value

# Label grouping level
F.when((F.grouping('a')==0) & (F.grouping('b')==0), 'detail')
 .when((F.grouping('a')==0) & (F.grouping('b')==1), 'a subtotal')
 .when((F.grouping('a')==1) & (F.grouping('b')==0), 'b subtotal')
 .otherwise('grand total')
```
