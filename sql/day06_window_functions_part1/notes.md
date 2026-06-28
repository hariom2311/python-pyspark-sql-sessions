# Day 6 — SQL: Window Functions Part 1 (ROW_NUMBER, RANK, DENSE_RANK)

> **Roadmap Day:** 6 · **Topics:** ROW_NUMBER · RANK · DENSE_RANK · PARTITION BY · ORDER BY  
> **Interview Level:** Easy → Medium

---

## 1. Why Window Functions?

Window functions compute a value **for each row** while still seeing all related rows (the "window"). Unlike `GROUP BY` which collapses rows into groups, window functions **keep every row** and add a new column.

**Classic use cases:**
- Rank employees by revenue within their region
- Top-N per group (top 2 salespeople per region)
- Find the #1 performer in any group

---

## 2. Syntax

```sql
function_name() OVER (
    PARTITION BY partition_col      -- defines the "group" (like GROUP BY)
    ORDER BY     sort_col DESC      -- defines the order within that group
)
```

`PARTITION BY` resets the function for each partition. `ORDER BY` determines ordering within each partition.

---

## 3. ROW_NUMBER — Always Unique

`ROW_NUMBER()` assigns 1, 2, 3, … within each partition. **No ties** — if two rows have the same ORDER BY value, one gets 1 and the other gets 2 (arbitrary tiebreak).

```sql
SELECT emp_id, region, revenue,
       ROW_NUMBER() OVER (PARTITION BY region ORDER BY revenue DESC) AS rn
FROM   sales;
```

Use when you need **exactly one row** per group (e.g. deduplicate, pick one arbitrarily).

---

## 4. RANK — Gaps After Ties

`RANK()` gives the same rank to tied rows, then **skips** the next rank number.

```
Revenue: 1000, 900, 900, 800
RANK:       1,   2,   2,   4   ← 3 is skipped
```

```sql
SELECT emp_id, region, revenue,
       RANK() OVER (PARTITION BY region ORDER BY revenue DESC) AS rnk
FROM   sales;
```

---

## 5. DENSE_RANK — No Gaps After Ties

`DENSE_RANK()` gives the same rank to tied rows but **does not skip** the next rank.

```
Revenue: 1000, 900, 900, 800
DENSE_RANK:  1,   2,   2,   3   ← no gap
```

```sql
SELECT emp_id, region, revenue,
       DENSE_RANK() OVER (PARTITION BY region ORDER BY revenue DESC) AS drnk
FROM   sales;
```

**Rule of thumb:**
- Use `RANK` when "gaps" matter (Olympic medals — no two silvers means no bronze)
- Use `DENSE_RANK` when you want consistent level numbering (top-N filtering — "give me rank ≤ 2" must always give 2 levels)

---

## 6. Filtering on Window Function Results — Use a CTE or Subquery

You **cannot** use a window function in a `WHERE` clause directly. Wrap it:

```sql
-- Get top 2 per region using DENSE_RANK
WITH ranked AS (
    SELECT emp_id, region, revenue,
           DENSE_RANK() OVER (PARTITION BY region ORDER BY revenue DESC) AS drnk
    FROM   sales
)
SELECT * FROM ranked WHERE drnk <= 2;
```

---

## 7. Day 6 Problem Solutions

### Q1 — Rank employees by revenue within each region
```sql
SELECT emp_id,
       region,
       month,
       revenue,
       RANK() OVER (PARTITION BY region ORDER BY revenue DESC) AS revenue_rank
FROM   d6_sales
ORDER  BY region, revenue_rank;
```

### Q2 — Top 2 employees per region (ties handled with DENSE_RANK)
```sql
WITH ranked AS (
    SELECT emp_id,
           region,
           revenue,
           DENSE_RANK() OVER (PARTITION BY region ORDER BY revenue DESC) AS drnk
    FROM   d6_sales
)
SELECT * FROM ranked WHERE drnk <= 2
ORDER  BY region, drnk;
```

### Q3 — Employees who ranked #1 in any region for any month
```sql
WITH ranked AS (
    SELECT emp_id,
           region,
           month,
           revenue,
           RANK() OVER (PARTITION BY region, month ORDER BY revenue DESC) AS rnk
    FROM   d6_sales
)
SELECT DISTINCT emp_id, region, month, revenue
FROM   ranked
WHERE  rnk = 1
ORDER  BY region, month;
```

---

## 8. Interview Checklist

- [ ] `OVER (PARTITION BY ...)` — defines the window (group); omitting it means the entire table is one window
- [ ] `ROW_NUMBER` — unique sequential numbers, no ties
- [ ] `RANK` — same number for ties, then skips next numbers (gaps)
- [ ] `DENSE_RANK` — same number for ties, NO gap
- [ ] Can't use window functions in `WHERE` — wrap in CTE or subquery
- [ ] `PARTITION BY` ≈ GROUP BY for window functions
- [ ] Can `PARTITION BY` multiple columns: `PARTITION BY region, month`

---

## 9. Quick Reference

| Function | Ties | Gap after ties | Use for |
|----------|------|----------------|---------|
| `ROW_NUMBER()` | No | — | Dedup, one-per-group |
| `RANK()` | Yes | Yes | Olympic-style ranking |
| `DENSE_RANK()` | Yes | No | Top-N filtering |

```sql
-- Template
SELECT *,
    ROW_NUMBER() OVER (PARTITION BY grp ORDER BY val DESC) AS rn,
    RANK()       OVER (PARTITION BY grp ORDER BY val DESC) AS rnk,
    DENSE_RANK() OVER (PARTITION BY grp ORDER BY val DESC) AS drnk
FROM table;

-- Filter top-N
WITH cte AS (SELECT *, DENSE_RANK() OVER (...) AS drnk FROM t)
SELECT * FROM cte WHERE drnk <= N;
```
