-- Day 3 SQL — Date & Time Functions
-- Run this script once to create all required tables.

-- ============================================================
-- 1. Notebook exploration table: orders
-- ============================================================
DROP TABLE IF EXISTS orders;

CREATE TABLE orders (
    order_id    SERIAL PRIMARY KEY,
    customer_id INTEGER        NOT NULL,
    order_date  DATE           NOT NULL,
    ship_date   DATE,
    amount      NUMERIC(10, 2) NOT NULL
);

INSERT INTO orders (customer_id, order_date, ship_date, amount) VALUES
-- Recent orders (within last 90 days from 2026-06-17)
(1001, '2026-05-01', '2026-05-05', 250.00),
(1002, '2026-05-03', '2026-05-14', 189.50),   -- slow: 11 days
(1001, '2026-05-10', '2026-05-17', 310.00),   -- slow: 7 days (edge)
(1003, '2026-05-15', '2026-05-23', 95.00),    -- slow: 8 days
(1004, '2026-05-20', '2026-05-21', 540.00),
(1002, '2026-06-01', '2026-06-03', 220.00),
(1005, '2026-06-05', '2026-06-19', 75.00),    -- slow: 14 days
(1003, '2026-06-10', '2026-06-12', 430.00),
(1006, '2026-06-12', '2026-06-14', 180.00),   -- new customer, recent first order
(1007, '2026-06-15', '2026-06-16', 99.00),    -- new customer, recent first order
-- Older orders (2025 — outside last 90 days)
(1001, '2025-01-05', '2025-01-07', 500.00),
(1002, '2025-03-12', '2025-03-14', 320.00),
(1003, '2025-06-20', '2025-07-01', 150.00),   -- slow: 11 days
(1004, '2025-09-08', '2025-09-10', 780.00),
(1005, '2025-11-25', '2025-11-30', 210.00),
(1001, '2025-12-01', '2025-12-15', 640.00),   -- slow: 14 days
(1002, '2025-12-20', '2025-12-22', 110.00),
(1004, '2026-01-10', '2026-01-12', 920.00),
(1001, '2026-02-14', '2026-02-16', 275.00),
(1003, '2026-03-01', '2026-03-04', 360.00),
(1002, '2026-03-18', '2026-03-20', 490.00),
(1005, '2026-04-05', '2026-04-07', 130.00);


-- ============================================================
-- 2. Practice Question tables (pq_ prefix)
-- ============================================================

-- pq_orders: same structure, same data — used for practice questions
DROP TABLE IF EXISTS pq_orders;

CREATE TABLE pq_orders (
    order_id    SERIAL PRIMARY KEY,
    customer_id INTEGER        NOT NULL,
    order_date  DATE           NOT NULL,
    ship_date   DATE,
    amount      NUMERIC(10, 2) NOT NULL
);

INSERT INTO pq_orders (customer_id, order_date, ship_date, amount)
SELECT customer_id, order_date, ship_date, amount FROM orders;


-- ============================================================
-- Verify
-- ============================================================
SELECT 'orders'    AS tbl, COUNT(*) AS rows FROM orders
UNION ALL
SELECT 'pq_orders' AS tbl, COUNT(*) AS rows FROM pq_orders;
