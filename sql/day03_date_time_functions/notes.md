# Day 3 — SQL: Date & Time Functions

> **Roadmap Day:** 3 · **Date:** Wednesday, June 17, 2026  
> **Study Window:** 9 PM – 11 PM  
> **Interview Level:** Easy → Medium

---

## 1. Why Dates Matter for Data Engineers

Almost every pipeline deals with dates:

- **Partitioning:** `WHERE order_date >= '2025-01-01'`
- **Reporting:** monthly/quarterly rollups
- **SLA checks:** `ship_date - order_date > 7`
- **Cohort analysis:** first-order date, tenure buckets

Mastering date functions is non-negotiable for DE interviews.

---

## 2. Date Arithmetic

### Subtract two dates → number of days

```sql
-- PostgreSQL: subtraction returns an integer
SELECT ship_date - order_date AS delivery_days
FROM   orders;

-- Cross-DB portable version using DATEDIFF:
-- MySQL / SQL Server
SELECT DATEDIFF(ship_date, order_date) AS delivery_days FROM orders;

-- DuckDB / BigQuery / Snowflake
SELECT DATE_DIFF('day', order_date, ship_date) AS delivery_days FROM orders;
```

### Add / subtract an interval

```sql
-- PostgreSQL
SELECT order_date + INTERVAL '7 days' AS expected_ship
FROM   orders;

SELECT NOW() - INTERVAL '90 days' AS start_of_window;

-- Shorthand
SELECT CURRENT_DATE - 90;   -- returns date 90 days ago
```

---

## 3. DATE_TRUNC — truncate to a calendar unit

```sql
-- Truncate to the first day of the month
SELECT DATE_TRUNC('month', order_date) AS order_month
FROM   orders;

-- Other units: 'year', 'quarter', 'week', 'day', 'hour', 'minute'

-- Use case: monthly revenue
SELECT DATE_TRUNC('month', order_date) AS month,
       SUM(amount)                     AS revenue
FROM   orders
GROUP  BY 1
ORDER  BY 1;
```

**Result:** every order maps to `YYYY-MM-01`, so aggregation is automatic.

---

## 4. EXTRACT / DATE_PART — pull a single field

```sql
-- EXTRACT (SQL standard)
SELECT EXTRACT(YEAR  FROM order_date) AS yr,
       EXTRACT(MONTH FROM order_date) AS mo,
       EXTRACT(DAY   FROM order_date) AS dy
FROM   orders;

-- DATE_PART (PostgreSQL alias)
SELECT DATE_PART('year',  order_date) AS yr,
       DATE_PART('month', order_date) AS mo
FROM   orders;

-- Use: group by year and month without DATE_TRUNC
SELECT EXTRACT(YEAR  FROM order_date) AS yr,
       EXTRACT(MONTH FROM order_date) AS mo,
       COUNT(*)                       AS num_orders
FROM   orders
GROUP  BY 1, 2
ORDER  BY 1, 2;
```

---

## 5. TO_CHAR — format a date as a string

```sql
-- PostgreSQL
SELECT TO_CHAR(order_date, 'YYYY-MM')  AS ym,
       TO_CHAR(order_date, 'Mon YYYY') AS label,
       TO_CHAR(order_date, 'DD/MM/YYYY') AS uk_fmt
FROM   orders;

-- Common format codes
-- YYYY  four-digit year        MM  two-digit month
-- Mon   abbreviated month name DD  two-digit day
-- HH24  24-h hour              MI  minutes    SS  seconds
```

---

## 6. CURRENT_DATE and NOW()

```sql
SELECT CURRENT_DATE;        -- date only, no time
SELECT NOW();               -- timestamp with time zone
SELECT CURRENT_TIMESTAMP;   -- alias for NOW()

-- Filter last 30 days
SELECT * FROM orders
WHERE  order_date >= CURRENT_DATE - 30;

-- Filter last 90 days (explicit interval)
SELECT * FROM orders
WHERE  order_date >= CURRENT_DATE - INTERVAL '90 days';
```

---

## 7. MIN / MAX on dates

```sql
-- First order per customer
SELECT customer_id,
       MIN(order_date) AS first_order_date,
       MAX(order_date) AS last_order_date
FROM   orders
GROUP  BY customer_id;
```

---

## 8. Day 3 SQL Problems

### Problem 1 (Easy) — Slow deliveries

Find all orders where delivery took more than 7 days.

```sql
SELECT order_id,
       customer_id,
       order_date,
       ship_date,
       ship_date - order_date AS delivery_days
FROM   orders
WHERE  ship_date - order_date > 7
ORDER  BY delivery_days DESC;
```

---

### Problem 2 (Easy) — Monthly revenue

Show total revenue by year-month, ordered chronologically.

```sql
SELECT TO_CHAR(order_date, 'YYYY-MM')     AS month,
       SUM(amount)                        AS total_revenue,
       COUNT(*)                           AS num_orders
FROM   orders
GROUP  BY DATE_TRUNC('month', order_date),
          TO_CHAR(order_date, 'YYYY-MM')
ORDER  BY DATE_TRUNC('month', order_date);
```

---

### Problem 3 (Medium) — New customers

Find customers whose **first** order was placed within the last 90 days from today.

```sql
SELECT customer_id,
       MIN(order_date) AS first_order_date,
       CURRENT_DATE - MIN(order_date) AS days_since_first_order
FROM   orders
GROUP  BY customer_id
HAVING MIN(order_date) >= CURRENT_DATE - INTERVAL '90 days'
ORDER  BY first_order_date DESC;
```

---

## 9. Common Gotchas

| Gotcha | Detail |
|--------|--------|
| `ship_date - order_date` in PostgreSQL | Returns integer (days). In MySQL, subtract dates gives integer too but use `DATEDIFF(a, b)`. |
| `DATE_TRUNC` returns a timestamp | Even if input is a `DATE`, output is `timestamp`. Cast back with `::date` if needed. |
| `CURRENT_DATE - 90` | PostgreSQL supports this shorthand; use `CURRENT_DATE - INTERVAL '90 days'` for clarity and portability. |
| `HAVING MIN(...)` | Aggregate filter belongs in `HAVING`, not `WHERE`. `WHERE` runs before grouping. |
| `TO_CHAR` GROUP BY | Always GROUP BY the `DATE_TRUNC` expression (sortable), not the `TO_CHAR` string, to get correct chronological ordering. |

---

## 10. Interview Checklist

| Question | Answer |
|----------|--------|
| Difference between `date_trunc` and `extract`? | `date_trunc` truncates to a calendar unit (e.g., first of month) and returns a date/timestamp. `extract` pulls a single integer field (year, month, etc.). |
| `WHERE` vs `HAVING` for date aggregates? | `WHERE` filters rows before aggregation. `HAVING` filters groups after aggregation (use for `MIN(order_date)`). |
| How to find rows from the last N days? | `WHERE order_date >= CURRENT_DATE - N` or `>= CURRENT_DATE - INTERVAL 'N days'`. |
| How to get monthly grouping? | `DATE_TRUNC('month', col)` or `EXTRACT(YEAR FROM col), EXTRACT(MONTH FROM col)`. |
| First order date per customer? | `MIN(order_date)` with `GROUP BY customer_id`. |

---

## 11. Quick Reference

```sql
-- Days between two dates (PostgreSQL)
ship_date - order_date

-- Add days to a date
order_date + INTERVAL '7 days'
order_date + 7          -- PostgreSQL shorthand

-- Today / now
CURRENT_DATE            -- date
NOW()                   -- timestamptz

-- Truncate to month
DATE_TRUNC('month', col)

-- Extract fields
EXTRACT(YEAR  FROM col)
EXTRACT(MONTH FROM col)
EXTRACT(DOW   FROM col)   -- day of week 0-6

-- Format as string
TO_CHAR(col, 'YYYY-MM')

-- Last 90 days filter
WHERE col >= CURRENT_DATE - INTERVAL '90 days'

-- Monthly revenue
SELECT DATE_TRUNC('month', order_date), SUM(amount)
FROM   orders
GROUP  BY 1  ORDER BY 1;

-- First order date
SELECT customer_id, MIN(order_date) AS first_order
FROM   orders GROUP BY customer_id;

-- New customers (first order in last 90 days)
HAVING MIN(order_date) >= CURRENT_DATE - INTERVAL '90 days'
```
