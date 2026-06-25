# Day 5 — SQL: All Joins

> **Roadmap Day:** 5 · **Date:** Friday, June 19, 2026  
> **Study Window:** 9 PM – 11 PM  
> **Interview Level:** Easy → Medium

---

## 1. Why Joins Matter for Data Engineers

Every analytical query joins tables — fact + dimension, orders + customers, employees + managers. Knowing which join to use and why is the single most-tested SQL skill in DE interviews.

---

## 2. The Six Join Types

```
customers        orders
C1  Alice        O1  C1  $100
C2  Bob          O2  C1  $200
C3  Carol        O3  C2  $300
                 O4  C9  $400   ← no matching customer
```

| Join | Returns |
|------|---------|
| `INNER JOIN` | Only rows that match on both sides |
| `LEFT JOIN` | All left rows + matching right (NULL if no match) |
| `RIGHT JOIN` | All right rows + matching left (NULL if no match) |
| `FULL OUTER JOIN` | All rows from both sides (NULL where no match) |
| `SELF JOIN` | Table joined to itself — manager hierarchies |
| `CROSS JOIN` | Every row × every row — Cartesian product |

---

## 3. INNER JOIN

Returns only rows where the join condition matches on **both** sides.

```sql
SELECT o.order_id, c.name, o.amount
FROM   orders   o
INNER  JOIN customers c ON o.customer_id = c.customer_id;
-- O4 ($400, C9) dropped — no matching customer
-- C3 Carol dropped — has no orders
```

---

## 4. LEFT JOIN

Returns **all rows from the left table** + matching right rows. Unmatched right side becomes NULL.

```sql
-- All customers, even those with no orders
SELECT c.name, o.order_id, o.amount
FROM   customers c
LEFT   JOIN orders o ON c.customer_id = o.customer_id;
-- Carol: order_id=NULL, amount=NULL

-- Find customers with NO orders
SELECT c.name
FROM   customers c
LEFT   JOIN orders o ON c.customer_id = o.customer_id
WHERE  o.order_id IS NULL;
```

---

## 5. RIGHT JOIN

Returns **all rows from the right table** + matching left rows. Rarely used — a LEFT JOIN with tables swapped is equivalent.

```sql
-- All orders, even those with no matching customer
SELECT c.name, o.order_id, o.amount
FROM   customers c
RIGHT  JOIN orders o ON c.customer_id = o.customer_id;
-- O4: name=NULL
```

---

## 6. FULL OUTER JOIN

Returns **all rows from both sides** — NULL where there is no match.

```sql
SELECT c.name, o.order_id, o.amount
FROM   customers c
FULL   OUTER JOIN orders o ON c.customer_id = o.customer_id;
-- Carol: order_id=NULL, amount=NULL
-- O4:   name=NULL
```

---

## 7. SELF JOIN

Join a table to **itself** — used for hierarchies (manager → employee).

```sql
-- employees(emp_id, name, manager_id)
SELECT e.name   AS employee,
       m.name   AS manager
FROM   employees e
LEFT   JOIN employees m ON e.manager_id = m.emp_id;
-- LEFT so CEO (no manager_id) still appears with NULL manager
```

---

## 8. CROSS JOIN

Produces a **Cartesian product** — every row paired with every other row.  
Result rows = rows_left × rows_right.

```sql
-- All size–colour combinations for a product
SELECT s.size, c.color
FROM   sizes  s
CROSS  JOIN colors c;
-- 3 sizes × 4 colors = 12 rows
```

Use sparingly — can produce massive result sets.

---

## 9. JOIN + GROUP BY (the DE pattern)

```sql
-- Total orders and revenue per customer — include customers with 0 orders
SELECT c.customer_id,
       c.name,
       COUNT(o.order_id)          AS total_orders,
       COALESCE(SUM(o.amount), 0) AS total_revenue
FROM   customers c
LEFT   JOIN orders o ON c.customer_id = o.customer_id
GROUP  BY c.customer_id, c.name
ORDER  BY total_revenue DESC;
```

Key: `COALESCE(SUM(...), 0)` — when no orders exist, SUM is NULL; COALESCE replaces it with 0.

---

## 10. Day 5 Problem Solutions

### Q1 — INNER JOIN orders + customers
```sql
SELECT o.order_id, c.name, o.amount
FROM   orders o
INNER  JOIN customers c ON o.customer_id = c.customer_id;
```

### Q2 — Customers with no orders (LEFT JOIN + IS NULL)
```sql
SELECT c.customer_id, c.name
FROM   customers c
LEFT   JOIN orders o ON c.customer_id = o.customer_id
WHERE  o.order_id IS NULL;
```

### Q3 — Total orders + revenue per customer including zeros
```sql
SELECT c.name,
       COUNT(o.order_id)          AS total_orders,
       COALESCE(SUM(o.amount), 0) AS total_revenue
FROM   customers c
LEFT   JOIN orders o ON c.customer_id = o.customer_id
GROUP  BY c.customer_id, c.name
ORDER  BY total_revenue DESC;
```

### Q4 — SELF JOIN: employee → manager
```sql
SELECT e.name AS employee, m.name AS manager
FROM   employees e
LEFT   JOIN employees m ON e.manager_id = m.emp_id;
```

### Q5 — FULL OUTER JOIN: unmatched on both sides
```sql
SELECT c.name, o.order_id, o.amount
FROM   customers c
FULL   OUTER JOIN orders o ON c.customer_id = o.customer_id
WHERE  c.customer_id IS NULL OR o.order_id IS NULL;
```

### Q6 — CROSS JOIN: all combinations
```sql
SELECT c.name AS customer, p.product_name
FROM   customers c
CROSS  JOIN products p;
```

---

## 11. Interview Checklist

- [ ] INNER vs LEFT — when does a row disappear?
- [ ] LEFT JOIN + IS NULL to find "not exists" rows
- [ ] COALESCE(SUM(...), 0) when including zero-order customers
- [ ] SELF JOIN: alias the same table twice (`e`, `m`)
- [ ] FULL OUTER JOIN — when both sides can have unmatched rows
- [ ] CROSS JOIN — Cartesian product, use it intentionally

---

## 12. Quick Reference

| Join | Keeps unmatched left? | Keeps unmatched right? |
|------|-----------------------|------------------------|
| INNER | ✗ | ✗ |
| LEFT | ✓ | ✗ |
| RIGHT | ✗ | ✓ |
| FULL OUTER | ✓ | ✓ |
| SELF | n/a — same table | n/a |
| CROSS | n/a — no condition | n/a |
