-- ============================================================
-- Day 4 — SQL Interview Problems
-- Topics: SELECT, Filters, CASE, JOINs, GROUP BY
-- This file is STANDALONE — run it top to bottom in one go.
-- ============================================================
-- Instructions for students:
--   1. Run the SETUP section first (creates tables + inserts data).
--   2. Read each problem carefully.
--   3. Write your answer in the space provided under each problem.
--   4. Expected output is shown so you can verify your result.
-- ============================================================


-- ============================================================
-- SETUP — Schema, Tables, Data
-- Run this entire block before attempting any problem.
-- ============================================================

DROP SCHEMA IF EXISTS store CASCADE;
CREATE SCHEMA store;

-- Customers
CREATE TABLE store.customers (
    customer_id   SERIAL PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    city          VARCHAR(50),
    tier          VARCHAR(20) CHECK (tier IN ('Bronze', 'Silver', 'Gold')),
    signup_date   DATE
);

-- Products
CREATE TABLE store.products (
    product_id    SERIAL PRIMARY KEY,
    product_name  VARCHAR(100) NOT NULL,
    category      VARCHAR(50),
    price         NUMERIC(10,2),
    stock         INT DEFAULT 0
);

-- Orders
CREATE TABLE store.orders (
    order_id      SERIAL PRIMARY KEY,
    customer_id   INT REFERENCES store.customers(customer_id),
    order_date    DATE NOT NULL,
    status        VARCHAR(20) CHECK (status IN ('pending', 'shipped', 'delivered', 'cancelled'))
);

-- Order Items
CREATE TABLE store.order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id      INT REFERENCES store.orders(order_id),
    product_id    INT REFERENCES store.products(product_id),
    quantity      INT NOT NULL,
    unit_price    NUMERIC(10,2) NOT NULL
);

-- Employees (sales reps)
CREATE TABLE store.employees (
    employee_id   SERIAL PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    department    VARCHAR(50),
    salary        NUMERIC(10,2),
    manager_id    INT REFERENCES store.employees(employee_id)
);

-- ---- Data Insertion ----

INSERT INTO store.customers (name, city, tier, signup_date) VALUES
    ('Alice Morgan',   'Mumbai',    'Gold',   '2021-03-15'),
    ('Bob Sharma',     'Pune',      'Silver', '2022-07-01'),
    ('Carol Nair',     'Mumbai',    'Bronze', '2023-01-20'),
    ('David Iyer',     'Bangalore', 'Gold',   '2020-11-10'),
    ('Eva Gupta',      'Pune',      'Silver', '2022-04-05'),
    ('Frank D''Souza', 'Mumbai',    'Bronze', '2023-06-30'),
    ('Grace Pillai',   'Hyderabad', 'Gold',   '2021-08-22'),
    ('Henry Rao',      NULL,        'Bronze', '2024-01-01');

INSERT INTO store.products (product_name, category, price, stock) VALUES
    ('Laptop Pro 15',   'Electronics', 85000.00, 20),
    ('Wireless Mouse',  'Electronics',  1200.00, 150),
    ('Office Chair',    'Furniture',   12000.00, 30),
    ('Standing Desk',   'Furniture',   25000.00, 10),
    ('Notebook Pack',   'Stationery',    350.00, 500),
    ('HDMI Cable',      'Electronics',   800.00, 200),
    ('Monitor 27"',     'Electronics', 22000.00, 25),
    ('Desk Lamp',       'Furniture',    2500.00, 80),
    ('Pen Set',         'Stationery',    150.00, 1000),
    ('Webcam HD',       'Electronics',  5500.00, 60);

INSERT INTO store.orders (customer_id, order_date, status) VALUES
    (1, '2024-01-10', 'delivered'),
    (1, '2024-03-05', 'delivered'),
    (2, '2024-02-14', 'shipped'),
    (3, '2024-01-25', 'cancelled'),
    (4, '2024-03-01', 'delivered'),
    (4, '2024-04-15', 'pending'),
    (5, '2024-02-28', 'delivered'),
    (6, '2024-03-10', 'shipped'),
    (7, '2024-01-05', 'delivered'),
    (7, '2024-04-20', 'delivered'),
    (8, '2024-02-01', 'pending');

INSERT INTO store.order_items (order_id, product_id, quantity, unit_price) VALUES
    (1, 1, 1, 85000.00),
    (1, 2, 2,  1200.00),
    (2, 7, 1, 22000.00),
    (3, 3, 1, 12000.00),
    (4, 5, 5,   350.00),
    (5, 1, 2, 85000.00),
    (5, 6, 3,   800.00),
    (6, 4, 1, 25000.00),
    (7, 2, 1,  1200.00),
    (8, 7, 1, 22000.00),
    (8, 8, 2,  2500.00),
    (9, 9, 10,  150.00),
    (10,10, 1,  5500.00),
    (10, 3, 1, 12000.00),
    (11, 5, 3,  350.00);

INSERT INTO store.employees (name, department, salary, manager_id) VALUES
    ('Sarah Lee',    'Sales',   95000.00, NULL),
    ('Tom Mathews',  'Sales',   72000.00, 1),
    ('Uma Verma',    'Sales',   68000.00, 1),
    ('Raj Patel',    'Support', 55000.00, NULL),
    ('Nina Singh',   'Support', 48000.00, 4),
    ('Oscar Mendes', 'Support', 52000.00, 4),
    ('Priya Kaur',   'Sales',   81000.00, 1),
    ('Quinn D''Cruz','Support', 45000.00, 4);


-- ============================================================
-- PROBLEMS
-- ============================================================


-- ------------------------------------------------------------
-- Problem 1 — SELECT + CASE
-- ------------------------------------------------------------
-- Write a query that returns every customer's name, city, tier,
-- and a new column called "tier_discount" showing:
--   Gold   → '15%'
--   Silver → '10%'
--   Bronze → '5%'
-- Customers with no city should show 'Unknown' for city.
--
-- Expected output (8 rows):
-- name            | city      | tier   | tier_discount
-- ----------------+-----------+--------+--------------
-- Alice Morgan    | Mumbai    | Gold   | 15%
-- David Iyer      | Bangalore | Gold   | 15%
-- Grace Pillai    | Hyderabad | Gold   | 15%
-- Bob Sharma      | Pune      | Silver | 10%
-- Eva Gupta       | Pune      | Silver | 10%
-- Carol Nair      | Mumbai    | Bronze | 5%
-- Frank D'Souza   | Mumbai    | Bronze | 5%
-- Henry Rao       | Unknown   | Bronze | 5%
-- ------------------------------------------------------------

-- YOUR ANSWER:


-- ------------------------------------------------------------
-- Problem 2 — Aggregation + GROUP BY + HAVING
-- ------------------------------------------------------------
-- Write a query that returns each product category with:
--   total_products  — how many products are in that category
--   avg_price       — average price rounded to 2 decimal places
--   total_stock     — sum of stock across all products in category
-- Show only categories where average price is above 5000.
-- Order by avg_price descending.
--
-- Expected output (2 rows):
-- category    | total_products | avg_price | total_stock
-- ------------+----------------+-----------+------------
-- Electronics |       5        | 22900.00  |  455
-- Furniture   |       3        | 13166.67  |  120
-- ------------------------------------------------------------

-- YOUR ANSWER:


-- ------------------------------------------------------------
-- Problem 3 — INNER JOIN
-- ------------------------------------------------------------
-- Write a query that returns each delivered order with:
--   order_id, customer name, order_date, and
--   order_total (sum of quantity × unit_price for that order).
-- Only include orders with status = 'delivered'.
-- Sort by order_total descending.
--
-- Expected output (6 rows):
-- order_id | name          | order_date | order_total
-- ---------+---------------+------------+------------
--        5 | David Iyer    | 2024-03-01 | 172400.00
--        1 | Alice Morgan  | 2024-01-10 |  87400.00
--        2 | Alice Morgan  | 2024-03-05 |  22000.00
--       10 | Grace Pillai  | 2024-04-20 |  17500.00
--        9 | Grace Pillai  | 2024-01-05 |   1500.00
--        7 | Eva Gupta     | 2024-02-28 |   1200.00
-- ------------------------------------------------------------

-- YOUR ANSWER:


-- ------------------------------------------------------------
-- Problem 4 — LEFT JOIN + anti-join pattern
-- ------------------------------------------------------------
-- Write a query that returns all customers who have NEVER
-- placed an order. Show customer_id, name, and city.
--
-- Expected output (0 rows from current data — all customers
-- have at least one order, so your query should return no rows.
-- Verify by checking: SELECT COUNT(DISTINCT customer_id) FROM store.orders → 8)
--
-- Hint: use LEFT JOIN + WHERE order_id IS NULL.
--
-- Expected output (0 rows):
-- customer_id | name | city
-- (no rows)
-- ------------------------------------------------------------

-- YOUR ANSWER:


-- ------------------------------------------------------------
-- Problem 5 — GROUP BY + CASE (conditional aggregation)
-- ------------------------------------------------------------
-- Write a query per customer showing:
--   name
--   total_orders     — total number of orders placed
--   delivered_count  — orders with status 'delivered'
--   cancelled_count  — orders with status 'cancelled'
-- Include all customers (even those with 0 delivered/cancelled).
-- Sort by total_orders descending.
--
-- Expected output (8 rows):
-- name           | total_orders | delivered_count | cancelled_count
-- ---------------+--------------+-----------------+----------------
-- Alice Morgan   |     2        |       2         |       0
-- David Iyer     |     2        |       1         |       0
-- Grace Pillai   |     2        |       2         |       0
-- Bob Sharma     |     1        |       0         |       0
-- Carol Nair     |     1        |       0         |       1
-- Eva Gupta      |     1        |       1         |       0
-- Frank D'Souza  |     1        |       0         |       0
-- Henry Rao      |     1        |       0         |       0
-- ------------------------------------------------------------

-- YOUR ANSWER:


-- ------------------------------------------------------------
-- Problem 6 — Multiple JOINs (3 tables)
-- ------------------------------------------------------------
-- Write a query that returns the top 3 best-selling products by
-- total revenue (quantity × unit_price across all order_items),
-- including only items from DELIVERED orders.
-- Show: product_name, category, total_revenue.
-- Sort by total_revenue descending.
--
-- Expected output (3 rows):
-- product_name   | category    | total_revenue
-- ---------------+-------------+--------------
-- Laptop Pro 15  | Electronics | 255000.00
-- Monitor 27"    | Electronics |  44000.00
-- Standing Desk  | Furniture   |  25000.00
-- ------------------------------------------------------------

-- YOUR ANSWER:


-- ------------------------------------------------------------
-- Problem 7 — SELF JOIN
-- ------------------------------------------------------------
-- Write a query that lists each employee's name and their
-- manager's name. Employees with no manager (top-level) should
-- still appear with NULL for manager_name.
-- Sort by employee name.
--
-- Expected output (8 rows):
-- employee_name | manager_name
-- --------------+--------------
-- Nina Singh    | Raj Patel
-- Oscar Mendes  | Raj Patel
-- Priya Kaur    | Sarah Lee
-- Quinn D'Cruz  | Raj Patel
-- Raj Patel     | NULL
-- Sarah Lee     | NULL
-- Tom Mathews   | Sarah Lee
-- Uma Verma     | Sarah Lee
-- ------------------------------------------------------------

-- YOUR ANSWER:


-- ------------------------------------------------------------
-- Problem 8 — Subquery in WHERE
-- ------------------------------------------------------------
-- Find all products whose price is above the average price
-- of their own category.
-- Show product_name, category, price, and the category's
-- avg_price (rounded to 2 decimal places).
-- Sort by category, then price descending.
--
-- Expected output (4 rows):
-- product_name   | category    | price     | avg_price
-- ---------------+-------------+-----------+-----------
-- Laptop Pro 15  | Electronics | 85000.00  | 22900.00
-- Monitor 27"    | Electronics | 22000.00  | 22900.00  ← wait, 22000 < 22900 — check the math
-- Standing Desk  | Furniture   | 25000.00  | 13166.67
-- Office Chair   | Furniture   | 12000.00  | 13166.67  ← 12000 < 13166.67 — this should NOT appear
--
-- Corrected expected output (3 rows):
-- product_name   | category    | price    | avg_price
-- ---------------+-------------+----------+-----------
-- Laptop Pro 15  | Electronics | 85000.00 | 22900.00
-- Standing Desk  | Furniture   | 25000.00 | 13166.67
-- Notebook Pack  | Stationery  |   350.00 |   250.00
-- ------------------------------------------------------------

-- YOUR ANSWER:


-- ------------------------------------------------------------
-- Problem 9 — FULL OUTER JOIN + CASE label
-- ------------------------------------------------------------
-- You have been given a second table of "priority_customers"
-- (created below). Write a FULL OUTER JOIN between customers
-- and priority_customers on customer_id, and label each row:
--   'Both'       — customer exists in both tables
--   'Store only' — customer exists only in store.customers
--   'List only'  — customer exists only in priority_customers
-- Show: customer_id (from either side), name (from either side),
--       and the label.

CREATE TABLE store.priority_customers (
    customer_id INT PRIMARY KEY,
    reason      VARCHAR(100)
);

INSERT INTO store.priority_customers VALUES
    (1, 'Top revenue'),
    (4, 'Top revenue'),
    (7, 'Loyalty program'),
    (9, 'Enterprise account'),    -- does NOT exist in store.customers
    (10, 'Enterprise account');   -- does NOT exist in store.customers

-- Expected output (10 rows):
-- customer_id | name          | label
-- ------------+---------------+------------
--           1 | Alice Morgan  | Both
--           2 | Bob Sharma    | Store only
--           3 | Carol Nair    | Store only
--           4 | David Iyer    | Both
--           5 | Eva Gupta     | Store only
--           6 | Frank D'Souza | Store only
--           7 | Grace Pillai  | Both
--           8 | Henry Rao     | Store only
--           9 | NULL          | List only
--          10 | NULL          | List only
-- ------------------------------------------------------------

-- YOUR ANSWER:


-- ------------------------------------------------------------
-- Problem 10 — Combined: JOINs + GROUP BY + CASE + Filter
-- ------------------------------------------------------------
-- Write a query that returns a summary per city showing:
--   city
--   customer_count  — number of customers in that city
--   total_orders    — total orders placed by customers from that city
--   total_revenue   — total revenue (quantity × unit_price) from
--                     their delivered orders only
--   city_tier       — 'High Value'   if total_revenue > 100000
--                     'Medium Value' if total_revenue > 20000
--                     'Low Value'    otherwise
-- Exclude customers with NULL city.
-- Sort by total_revenue descending.
--
-- Expected output (4 rows):
-- city      | customer_count | total_orders | total_revenue | city_tier
-- ----------+----------------+--------------+---------------+----------
-- Mumbai    |       3        |      4       |   109400.00   | High Value
-- Bangalore |       1        |      2       |   172400.00   | High Value
-- Pune      |       2        |      2       |     1200.00   | Low Value
-- Hyderabad |       1        |      2       |    17500.00   | Low Value
-- ------------------------------------------------------------

-- YOUR ANSWER:
