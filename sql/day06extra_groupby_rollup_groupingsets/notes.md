# Day 6 — SQL: GROUP BY, GROUPING SETS, ROLLUP

> **Roadmap Day:** 6 · **Date:** Saturday, June 21, 2026  
> **Study Window:** 9 PM – 11 PM  
> **Interview Level:** Easy → Medium

---

## 1. Why These Matter for Data Engineers

Reporting queries need subtotals at multiple levels — region total, category total, grand total — all in one pass. `ROLLUP` and `GROUPING SETS` replace multiple `UNION ALL` queries with a single efficient scan.

---

## 2. Basic GROUP BY (Recap)

```sql
SELECT region, category, SUM(revenue) AS total_revenue
FROM   sales
GROUP  BY region, category
ORDER  BY region, category;
-- One row per (region, category) combination
```

---

## 3. ROLLUP — Hierarchical Subtotals

`ROLLUP(a, b)` produces:
1. `(a, b)` — lowest level detail
2. `(a)` — subtotal per a
3. `()` — grand total

```sql
SELECT region, category,
       SUM(revenue) AS total_revenue
FROM   sales
GROUP  BY ROLLUP(region, category)
ORDER  BY region NULLS LAST, category NULLS LAST;
```

**NULL in the result = that level was rolled up.** A NULL `category` with a non-NULL `region` means "subtotal for that region across all categories."

Use `GROUPING()` to distinguish NULL-from-data vs NULL-from-rollup:
```sql
SELECT
    CASE WHEN GROUPING(region)   = 1 THEN 'ALL REGIONS'   ELSE region   END AS region,
    CASE WHEN GROUPING(category) = 1 THEN 'ALL CATEGORIES' ELSE category END AS category,
    SUM(revenue) AS total_revenue
FROM   sales
GROUP  BY ROLLUP(region, category);
```

---

## 4. GROUPING SETS — Custom Combinations

`GROUPING SETS` lets you pick exactly which grouping combinations you want — no extras.

```sql
-- Produces: (region, category), (region only), (category only), grand total
SELECT region, category, SUM(revenue) AS total_revenue
FROM   sales
GROUP  BY GROUPING SETS (
    (region, category),   -- detail level
    (region),             -- region subtotal
    (category),           -- category subtotal
    ()                    -- grand total
)
ORDER  BY region NULLS LAST, category NULLS LAST;
```

**ROLLUP vs GROUPING SETS:**
- `ROLLUP(region, category)` ≡ `GROUPING SETS((region,category), (region), ())`
- Use `ROLLUP` for strict hierarchy; use `GROUPING SETS` when you need cross-dimension subtotals (like both region-only AND category-only)

---

## 5. CUBE — All Possible Combinations

```sql
-- CUBE(region, category) produces ALL possible groupings:
-- (region, category), (region), (category), ()
SELECT region, category, SUM(revenue)
FROM   sales
GROUP  BY CUBE(region, category);
-- Same as GROUPING SETS((region,category),(region),(category),())
```

---

## 6. Day 6 Problem Solutions

### Q1 — Total revenue by region and category
```sql
SELECT region,
       category,
       SUM(revenue) AS total_revenue
FROM   d6_sales
GROUP  BY region, category
ORDER  BY region, category;
```

### Q2 — ROLLUP: region → category → grand total
```sql
SELECT
    COALESCE(region,   'ALL REGIONS')    AS region,
    COALESCE(category, 'ALL CATEGORIES') AS category,
    SUM(revenue) AS total_revenue
FROM   d6_sales
GROUP  BY ROLLUP(region, category)
ORDER  BY region NULLS LAST, category NULLS LAST;
```

### Q3 — GROUPING SETS: (region), (category), (region, category)
```sql
SELECT
    COALESCE(region,   'ALL')  AS region,
    COALESCE(category, 'ALL')  AS category,
    SUM(revenue)               AS total_revenue,
    CASE
        WHEN GROUPING(region) = 0 AND GROUPING(category) = 0 THEN 'region+category'
        WHEN GROUPING(region) = 0                             THEN 'region only'
        WHEN GROUPING(category) = 0                           THEN 'category only'
        ELSE 'grand total'
    END AS grouping_level
FROM   d6_sales
GROUP  BY GROUPING SETS (
    (region, category),
    (region),
    (category)
)
ORDER  BY grouping_level, region NULLS LAST, category NULLS LAST;
```

---

## 7. Interview Checklist

- [ ] GROUP BY multiple columns — one row per unique combination
- [ ] ROLLUP — hierarchical subtotals, NULL = rolled-up level
- [ ] GROUPING() function — distinguish rollup-NULLs from data-NULLs
- [ ] COALESCE on rolled-up columns to label subtotal rows
- [ ] GROUPING SETS — pick exactly which levels you need
- [ ] CUBE — all possible grouping combinations
- [ ] ROLLUP(a,b) ≡ GROUPING SETS((a,b),(a),())

---

## 8. Quick Reference

| Feature | Syntax | Produces |
|---------|--------|---------|
| Basic GROUP BY | `GROUP BY a, b` | One row per (a, b) |
| ROLLUP | `GROUP BY ROLLUP(a, b)` | (a,b) + (a) + () |
| GROUPING SETS | `GROUP BY GROUPING SETS((a,b),(a),(b),())` | Custom levels |
| CUBE | `GROUP BY CUBE(a, b)` | All 4 combinations |
| Label rollup NULLs | `COALESCE(col, 'ALL')` | Replace NULL with label |
| Detect rollup level | `GROUPING(col)` = 1 means rolled up | 0 = real value |
