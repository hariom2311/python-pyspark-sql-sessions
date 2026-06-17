-- =============================================================
-- Day 2 — SQL String Functions
-- Dataset: customers with intentionally messy data
-- =============================================================

-- Main practice table
DROP TABLE IF EXISTS customers CASCADE;

CREATE TABLE customers (
    customer_id  INT PRIMARY KEY,
    full_name    VARCHAR(100),
    email        VARCHAR(150),
    phone        VARCHAR(30),
    address      VARCHAR(200)
);

-- Intentionally messy: mixed case, leading/trailing spaces, varied phone formats
INSERT INTO customers VALUES
(1,  '  Alice Johnson  ',  'ALICE@Gmail.COM   ',  '  +91-98765-43210 ', '12, MG Road, Mumbai'),
(2,  'bob smith',           'bob@yahoo.com',       '9876100002',         '45 Park Street, Delhi'),
(3,  'CAROL WHITE',         ' carol@hotmail.com',  '(098) 761-00003',    '7/B Lake View, Chennai'),
(4,  'David Brown',         'david@gmail.com',     '987.610.0004',       '22 Hill Top, Pune'),
(5,  'eve nair  ',          'EVE@GMAIL.COM',       '+919876100005',      '8 MG Road, Bangalore'),
(6,  'Frank Singh',         'frank@outlook.com',   '98-7610-0006',       '33 Nehru Place, Hyderabad'),
(7,  'GRACE PATEL',         'GRACE@yahoo.com ',    '9876100007',         '15 Ring Road, Kolkata'),
(8,  '  henry das',         'henry@gmail.com',     '(987) 610-0008',     '9 Carter Road, Ahmedabad'),
(9,  'Irene Verma',         'irene@gmail.COM',     '9876100009  ',       '5 Civil Lines, Jaipur'),
(10, 'jack KUMAR',          'JACK@hotmail.com',    '987-610-0010',       '18 Anna Nagar, Surat');


-- =============================================================
-- Practice Questions tables (each Q has its own table)
-- =============================================================

-- Q1 table: products with messy names and categories
DROP TABLE IF EXISTS pq_products CASCADE;

CREATE TABLE pq_products (
    product_id   INT PRIMARY KEY,
    product_name VARCHAR(100),
    category     VARCHAR(50),
    sku          VARCHAR(30),
    price        NUMERIC(10,2)
);

INSERT INTO pq_products VALUES
(1,  '  Laptop Pro 15  ',    'ELECTRONICS',     'LP-15-2024',  85000.00),
(2,  'wireless MOUSE',       'Electronics',     'WM-001-BLK',  1500.00),
(3,  'MECHANICAL Keyboard',  'electronics',     'MK-TKL-2023', 4500.00),
(4,  '  USB-C Hub   ',       'Accessories',     'UC-HUB-7P',   2200.00),
(5,  'noise Cancelling headphones', 'ELECTRONICS', 'NCH-PRO-X', 12000.00),
(6,  'Cotton T-Shirt  ',     'CLOTHING',        'CTS-M-WHT',   599.00),
(7,  '  DENIM JEANS',        'Clothing',        'DJ-32-BLU',   1999.00),
(8,  'running shoes  ',      'clothing',        'RS-42-BLK',   3499.00),
(9,  'Python Programming',   'BOOKS',           'BK-PY-ADV',   799.00),
(10, '  data engineering handbook', 'Books',    'BK-DE-2024',  1299.00),
(11, 'Yoga Mat',             'SPORTS',          'YM-6MM-PRP',  1199.00),
(12, '  Dumbbell Set  ',     'sports',          'DB-10KG-SET',  3999.00);


-- Q2 table: user accounts with malformed contact info
DROP TABLE IF EXISTS pq_user_accounts CASCADE;

CREATE TABLE pq_user_accounts (
    user_id        INT PRIMARY KEY,
    username       VARCHAR(50),
    email          VARCHAR(150),
    phone          VARCHAR(30),
    country_code   VARCHAR(5),
    account_status VARCHAR(20)
);

INSERT INTO pq_user_accounts VALUES
(1,  'alice_j',    'alice@gmail.com',         '+91-9876543210', 'IN', 'active'),
(2,  'bob_s',      'bob AT yahoo DOT com',    '9876543211',     'IN', 'active'),    -- bad email
(3,  'carol_w',    'carol@hotmail.com',        'abcd-efgh',      'US', 'active'),    -- non-digit phone
(4,  'dave_b',     'david@gmail',              '+1-5559876543',  'US', 'active'),    -- no TLD in email
(5,  'eve_n',      'eve@gmail.com',            '9876543214',     'IN', 'inactive'),
(6,  'frank_s',    'frank@outlook.com',        '(+44) 7911123456', 'UK', 'active'),
(7,  'grace_p',    'GRACE yahoo com',          '9876543216',     'IN', 'active'),    -- no @ in email
(8,  'henry_d',    'henry@gmail.com',          '987654321',      'IN', 'active'),    -- only 9 digits
(9,  'irene_v',    'irene@gmail.com',          '+91-9876543218', 'IN', 'active'),
(10, 'jack_k',     'jack@',                    '9876543219',     'IN', 'active');    -- email ends with @


-- Q3 table: raw transaction log (pipe-delimited text in one column)
DROP TABLE IF EXISTS pq_raw_transactions CASCADE;

CREATE TABLE pq_raw_transactions (
    log_id   INT PRIMARY KEY,
    log_line VARCHAR(500)
);

INSERT INTO pq_raw_transactions VALUES
(1,  '2024-01-15|TXN-001|CREDIT|  Alice Johnson  |5000.00|SUCCESS'),
(2,  '2024-01-15|TXN-002|DEBIT |bob smith        |1200.50|SUCCESS'),
(3,  '2024-01-16|TXN-003|CREDIT|  CAROL WHITE    |8750.00|FAILED '),
(4,  '2024-01-16|TXN-004|DEBIT |David Brown      |300.00 |SUCCESS'),
(5,  '2024-01-17|TXN-005|CREDIT|eve nair         |  2500.00|PENDING'),
(6,  '2024-01-17|TXN-006|DEBIT |  Frank Singh    |650.75 |SUCCESS'),
(7,  '2024-01-18|TXN-007|CREDIT|GRACE PATEL      |11000.00|SUCCESS'),
(8,  '2024-01-18|TXN-008|DEBIT |henry das        |450.00 |FAILED '),
(9,  '2024-01-19|TXN-009|CREDIT|  Irene Verma    |3300.00|SUCCESS'),
(10, '2024-01-19|TXN-010|DEBIT |jack KUMAR       |900.25 |PENDING');


-- =============================================================
-- Quick verification
-- =============================================================
-- SELECT 'customers'         AS tbl, COUNT(*) FROM customers;
-- SELECT 'pq_products'       AS tbl, COUNT(*) FROM pq_products;
-- SELECT 'pq_user_accounts'  AS tbl, COUNT(*) FROM pq_user_accounts;
-- SELECT 'pq_raw_transactions' AS tbl, COUNT(*) FROM pq_raw_transactions;
