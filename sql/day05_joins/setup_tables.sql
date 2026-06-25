-- Day 5 SQL — All Joins: Setup Tables
-- Run this in DBeaver / psql before opening the notebooks
-- Target: PostgreSQL localhost:5432 database: practice_db

-- ── Drop and recreate ────────────────────────────────────────────────────────
DROP TABLE IF EXISTS orders     CASCADE;
DROP TABLE IF EXISTS customers  CASCADE;
DROP TABLE IF EXISTS employees  CASCADE;
DROP TABLE IF EXISTS products   CASCADE;

-- ── customers ────────────────────────────────────────────────────────────────
CREATE TABLE customers (
    customer_id   SERIAL PRIMARY KEY,
    name          VARCHAR(50)    NOT NULL,
    email         VARCHAR(100),
    city          VARCHAR(50)
);

INSERT INTO customers (name, email, city) VALUES
    ('Alice',  'alice@example.com',  'New York'),
    ('Bob',    'bob@example.com',    'Chicago'),
    ('Carol',  'carol@example.com',  'Houston'),
    ('Dave',   'dave@example.com',   'Phoenix'),
    ('Eve',    'eve@example.com',    'Seattle');

-- ── orders ───────────────────────────────────────────────────────────────────
-- Note: customer_id 99 is intentionally orphaned (no matching customer)
CREATE TABLE orders (
    order_id     SERIAL PRIMARY KEY,
    customer_id  INT,              -- no FK so we can test FULL OUTER with orphans
    amount       NUMERIC(10, 2)   NOT NULL,
    status       VARCHAR(20)      DEFAULT 'pending',
    order_date   DATE             NOT NULL
);

INSERT INTO orders (customer_id, amount, status, order_date) VALUES
    (1, 250.00, 'completed', '2024-01-05'),
    (1, 125.50, 'pending',   '2024-01-12'),
    (2, 89.99,  'completed', '2024-01-07'),
    (3, 450.00, 'completed', '2024-01-10'),
    (3, 210.00, 'cancelled', '2024-01-14'),
    (5, 320.00, 'completed', '2024-01-08'),
    (99, 75.00, 'pending',   '2024-01-15');  -- orphan: no customer_id=99

-- customer_id 4 (Dave) has no orders → will show as NULL in LEFT JOIN

-- ── employees (self-join hierarchy) ──────────────────────────────────────────
CREATE TABLE employees (
    emp_id      SERIAL PRIMARY KEY,
    name        VARCHAR(50)  NOT NULL,
    role        VARCHAR(50),
    manager_id  INT          REFERENCES employees(emp_id)   -- self-reference
);

INSERT INTO employees (name, role, manager_id) VALUES
    ('Sarah',  'CEO',           NULL),   -- emp_id=1, no manager
    ('Tom',    'VP Engineering',   1),   -- emp_id=2, reports to Sarah
    ('Priya',  'VP Marketing',     1),   -- emp_id=3, reports to Sarah
    ('Alice',  'Engineer',         2),   -- emp_id=4, reports to Tom
    ('Bob',    'Engineer',         2),   -- emp_id=5, reports to Tom
    ('Carol',  'Designer',         3),   -- emp_id=6, reports to Priya
    ('Dave',   'Analyst',          3);   -- emp_id=7, reports to Priya

-- ── products (for CROSS JOIN) ────────────────────────────────────────────────
CREATE TABLE products (
    product_id    SERIAL PRIMARY KEY,
    product_name  VARCHAR(50)  NOT NULL,
    category      VARCHAR(30),
    price         NUMERIC(8, 2)
);

INSERT INTO products (product_name, category, price) VALUES
    ('Widget A',  'Hardware',  29.99),
    ('Widget B',  'Hardware',  49.99),
    ('Service X', 'Software',  99.00),
    ('Service Y', 'Software', 149.00);

-- ── Verify ───────────────────────────────────────────────────────────────────
SELECT 'customers' AS tbl, COUNT(*) FROM customers
UNION ALL
SELECT 'orders',    COUNT(*) FROM orders
UNION ALL
SELECT 'employees', COUNT(*) FROM employees
UNION ALL
SELECT 'products',  COUNT(*) FROM products;
