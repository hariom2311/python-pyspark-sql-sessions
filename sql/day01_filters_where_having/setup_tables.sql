-- ============================================================
-- SQL Notes — Table Creation & Sample Data
-- Works with: PostgreSQL (primary) | MySQL compatible where noted
-- Run this first, then practise all queries from the .md notes
-- ============================================================

-- ============================================================
-- SECTION 1: CORE BUSINESS TABLES
-- Used across: 01, 02, 03, 04, 05, 06, 07, 08, 09, 10
-- ============================================================

DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS employees CASCADE;
DROP TABLE IF EXISTS departments CASCADE;
DROP TABLE IF EXISTS locations CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS sales CASCADE;
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS events CASCADE;

-- locations
CREATE TABLE locations (
    id       SERIAL PRIMARY KEY,
    city     VARCHAR(100),
    state    VARCHAR(100),
    country  VARCHAR(100)
);

INSERT INTO locations (city, state, country) VALUES
('Mumbai',    'Maharashtra', 'India'),
('Delhi',     'Delhi',       'India'),
('Bangalore', 'Karnataka',   'India'),
('Chennai',   'Tamil Nadu',  'India'),
('Hyderabad', 'Telangana',   'India'),
('Pune',      'Maharashtra', 'India');

-- departments
CREATE TABLE departments (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100),
    location_id     INT REFERENCES locations(id),
    budget          NUMERIC(12,2),
    active          BOOLEAN DEFAULT TRUE
);

INSERT INTO departments (name, location_id, budget, active) VALUES
('Engineering',  1, 5000000.00, TRUE),
('Finance',      2, 2000000.00, TRUE),
('HR',           3, 1500000.00, TRUE),
('Marketing',    4, 1800000.00, TRUE),
('Operations',   5, 2500000.00, TRUE),
('Legal',        6,  800000.00, FALSE);

-- employees
CREATE TABLE employees (
    id             SERIAL PRIMARY KEY,
    name           VARCHAR(100),
    email          VARCHAR(150),
    department     VARCHAR(100),
    department_id  INT REFERENCES departments(id),
    job_title      VARCHAR(100),
    salary         NUMERIC(10,2),
    bonus          NUMERIC(10,2),
    manager_id     INT,
    hire_date      DATE,
    status         VARCHAR(20) DEFAULT 'active',
    gender         CHAR(1),
    age            INT,
    phone          VARCHAR(20)
);

INSERT INTO employees (name, email, department, department_id, job_title, salary, bonus, manager_id, hire_date, status, gender, age, phone) VALUES
('Alice Johnson',  'alice@company.com',   'Engineering', 1, 'Senior Engineer',   95000, 8000,  NULL, '2019-03-15', 'active',   'F', 32, '9876543210'),
('Bob Smith',      'bob@company.com',     'Engineering', 1, 'Junior Engineer',   65000, 3000,  1,    '2021-07-01', 'active',   'M', 26, '9876543211'),
('Carol White',    'carol@company.com',   'Finance',     2, 'Finance Manager',   85000, 7000,  NULL, '2018-01-10', 'active',   'F', 38, '9876543212'),
('Dave Brown',     'dave@company.com',    'Finance',     2, 'Analyst',           60000, 2500,  3,    '2022-04-20', 'active',   'M', 28, '9876543213'),
('Eve Davis',      'eve@company.com',     'HR',          3, 'HR Manager',        75000, 5000,  NULL, '2017-06-05', 'active',   'F', 41, '9876543214'),
('Frank Miller',   'frank@company.com',   'HR',          3, 'HR Executive',      50000, 1500,  5,    '2023-01-15', 'active',   'M', 24, NULL),
('Grace Wilson',   'grace@company.com',   'Marketing',   4, 'Marketing Lead',    80000, 6000,  NULL, '2020-09-01', 'active',   'F', 35, '9876543216'),
('Henry Moore',    'henry@company.com',   'Marketing',   4, 'Marketing Exec',    55000, 2000,  7,    '2022-11-10', 'inactive', 'M', 29, '9876543217'),
('Iris Taylor',    'iris@company.com',    'Engineering', 1, 'Staff Engineer',   110000,10000,  1,    '2016-02-28', 'active',   'F', 40, '9876543218'),
('Jack Anderson',  'jack@company.com',    'Operations',  5, 'Ops Manager',       72000, 4000,  NULL, '2019-08-12', 'active',   'M', 36, '9876543219'),
('Karen Thomas',   'karen@company.com',   'Operations',  5, 'Ops Analyst',       48000, 1000,  10,   '2023-03-01', 'active',   'F', 23, '9876543220'),
('Leo Jackson',    'leo@company.com',     'Engineering', 1, 'Engineer',          78000, 5500,  1,    '2020-05-17', 'active',   'M', 30, '9876543221'),
('Mia Harris',     'mia@company.com',     'Finance',     2, 'Senior Analyst',    70000, 4500,  3,    '2021-02-28', 'active',   'F', 33, '9876543222'),
('Nathan Clark',   'nathan@company.com',  'Marketing',   4, 'Content Writer',    45000,  800,  7,    '2023-06-01', 'active',   'M', 22, '9876543223'),
('Olivia Lewis',   'olivia@company.com',  'HR',          3, 'Recruiter',         52000, 1800,  5,    '2022-08-15', 'active',   'F', 27, '9876543224');

-- customers
CREATE TABLE customers (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100),
    email       VARCHAR(150),
    city        VARCHAR(100),
    country     VARCHAR(100),
    signup_date DATE,
    status      VARCHAR(20) DEFAULT 'active'
);

INSERT INTO customers (name, email, city, country, signup_date, status) VALUES
('Rahul Sharma',   'rahul@gmail.com',   'Mumbai',    'India', '2022-01-05', 'active'),
('Priya Patel',    'priya@gmail.com',   'Delhi',     'India', '2022-03-12', 'active'),
('Amit Verma',     'amit@yahoo.com',    'Bangalore', 'India', '2021-11-20', 'active'),
('Sneha Nair',     'sneha@gmail.com',   'Chennai',   'India', '2023-02-14', 'active'),
('Rohan Gupta',    'rohan@hotmail.com', 'Pune',      'India', '2022-07-30', 'inactive'),
('Meera Singh',    'meera@gmail.com',   'Hyderabad', 'India', '2023-05-01', 'active'),
('Vikram Joshi',   'vikram@gmail.com',  'Mumbai',    'India', '2021-09-08', 'active'),
('Ananya Das',     'ananya@gmail.com',  'Kolkata',   'India', '2022-12-25', 'active'),
('Sanjay Kumar',   'sanjay@yahoo.com',  'Delhi',     'India', '2020-06-15', 'active'),
('Divya Reddy',    'divya@gmail.com',   'Bangalore', 'India', '2023-08-10', 'active');

-- products
CREATE TABLE products (
    id           SERIAL PRIMARY KEY,
    name         VARCHAR(150),
    category     VARCHAR(100),
    price        NUMERIC(10,2),
    cost         NUMERIC(10,2),
    stock        INT,
    low_fats     CHAR(1) DEFAULT 'N',
    recyclable   CHAR(1) DEFAULT 'N',
    created_at   DATE DEFAULT CURRENT_DATE
);

INSERT INTO products (name, category, price, cost, stock, low_fats, recyclable) VALUES
('Laptop Pro 15',      'Electronics',  75000, 55000, 50,  'N', 'N'),
('Wireless Mouse',     'Electronics',   1500,   800, 200, 'N', 'Y'),
('Office Chair',       'Furniture',    12000,  7000, 30,  'N', 'N'),
('Standing Desk',      'Furniture',    25000, 15000, 15,  'N', 'Y'),
('Python Book',        'Books',          600,   200, 300, 'Y', 'Y'),
('SQL Guide',          'Books',          500,   150, 250, 'Y', 'Y'),
('Mechanical Keyboard','Electronics',   4500,  2500, 80,  'N', 'N'),
('USB Hub 7-Port',     'Electronics',   2000,  1000, 120, 'Y', 'Y'),
('Notebook Pack',      'Stationery',     200,    80, 500, 'Y', 'Y'),
('Webcam HD',          'Electronics',   3500,  2000, 60,  'N', 'Y');

-- orders
CREATE TABLE orders (
    id              SERIAL PRIMARY KEY,
    customer_id     INT REFERENCES customers(id),
    product_id      INT REFERENCES products(id),
    quantity        INT,
    unit_price      NUMERIC(10,2),
    amount          NUMERIC(10,2),
    order_date      DATE,
    status          VARCHAR(20) DEFAULT 'completed',
    employee_id     INT REFERENCES employees(id)
);

INSERT INTO orders (customer_id, product_id, quantity, unit_price, amount, order_date, status, employee_id) VALUES
(1,  1, 1, 75000, 75000, '2024-01-05', 'completed', 1),
(2,  2, 3,  1500,  4500, '2024-01-08', 'completed', 2),
(3,  5, 2,   600,  1200, '2024-01-10', 'completed', 1),
(4,  3, 1, 12000, 12000, '2024-01-15', 'completed', 7),
(1,  7, 1,  4500,  4500, '2024-01-18', 'completed', 1),
(5,  4, 1, 25000, 25000, '2024-02-01', 'pending',   10),
(6,  8, 2,  2000,  4000, '2024-02-05', 'completed', 1),
(7,  2, 5,  1500,  7500, '2024-02-10', 'completed', 2),
(8,  6, 3,   500,  1500, '2024-02-14', 'completed', 1),
(9,  1, 2, 75000,150000, '2024-02-20', 'completed', 12),
(10, 9,10,   200,  2000, '2024-03-01', 'completed', 1),
(1,  3, 1, 12000, 12000, '2024-03-05', 'completed', 7),
(2,  1, 1, 75000, 75000, '2024-03-12', 'completed', 1),
(3,  7, 2,  4500,  9000, '2024-03-18', 'completed', 12),
(4, 10, 1,  3500,  3500, '2024-04-01', 'cancelled', 1),
(6,  5, 4,   600,  2400, '2024-04-05', 'completed', 1),
(7,  4, 1, 25000, 25000, '2024-04-10', 'completed', 10),
(8,  8, 3,  2000,  6000, '2024-04-15', 'completed', 1),
(9,  2, 2,  1500,  3000, '2024-05-01', 'completed', 2),
(10, 6, 2,   500,  1000, '2024-05-10', 'completed', 1);

-- sales (daily aggregated sales — used for time series examples)
CREATE TABLE sales (
    id           SERIAL PRIMARY KEY,
    product_id   INT REFERENCES products(id),
    sale_date    DATE,
    quantity     INT,
    amount       NUMERIC(10,2),
    region       VARCHAR(50),
    channel      VARCHAR(50)
);

INSERT INTO sales (product_id, sale_date, quantity, amount, region, channel) VALUES
(1, '2024-01-02',  2, 150000, 'North', 'online'),
(2, '2024-01-02', 10,  15000, 'South', 'online'),
(3, '2024-01-03',  1,  12000, 'East',  'offline'),
(1, '2024-01-05',  1,  75000, 'West',  'online'),
(5, '2024-01-08', 20,  12000, 'North', 'online'),
(2, '2024-01-10', 15,  22500, 'South', 'offline'),
(4, '2024-02-01',  2,  50000, 'East',  'online'),
(7, '2024-02-03',  5,  22500, 'North', 'online'),
(1, '2024-02-15',  3, 225000, 'West',  'online'),
(6, '2024-02-20', 30,  15000, 'South', 'online'),
(3, '2024-03-01',  4,  48000, 'North', 'offline'),
(8, '2024-03-10', 12,  24000, 'East',  'online'),
(1, '2024-03-20',  1,  75000, 'South', 'online'),
(5, '2024-04-01', 50,  30000, 'North', 'online'),
(2, '2024-04-15', 20,  30000, 'West',  'offline'),
(9, '2024-05-01',100,  20000, 'East',  'online'),
(1, '2024-05-10',  2, 150000, 'North', 'online'),
(7, '2024-05-20',  8,  36000, 'South', 'online');

-- transactions (financial transactions with status — used in date/time, window, cleaning)
CREATE TABLE transactions (
    id              SERIAL PRIMARY KEY,
    user_id         INT,
    account_id      INT,
    amount          NUMERIC(10,2),
    trans_type      VARCHAR(20),   -- 'credit' / 'debit'
    status          VARCHAR(20),   -- 'approved' / 'declined'
    trans_date      DATE,
    created_at      TIMESTAMP DEFAULT NOW()
);

INSERT INTO transactions (user_id, account_id, amount, trans_type, status, trans_date) VALUES
(1,  101,  5000, 'credit', 'approved',  '2024-01-03'),
(1,  101,  2000, 'debit',  'approved',  '2024-01-10'),
(2,  102, 15000, 'credit', 'approved',  '2024-01-05'),
(2,  102,  8000, 'debit',  'approved',  '2024-01-20'),
(3,  103,   500, 'debit',  'declined',  '2024-02-01'),
(3,  103, 12000, 'credit', 'approved',  '2024-02-05'),
(4,  104,  3000, 'debit',  'approved',  '2024-02-08'),
(1,  101,  7000, 'credit', 'approved',  '2024-02-15'),
(5,  105, 25000, 'credit', 'approved',  '2024-03-01'),
(5,  105, 10000, 'debit',  'approved',  '2024-03-10'),
(2,  102,  4000, 'debit',  'approved',  '2024-03-20'),
(6,  106,  8000, 'credit', 'approved',  '2024-04-01'),
(3,  103,  6000, 'debit',  'approved',  '2024-04-05'),
(4,  104, 20000, 'credit', 'approved',  '2024-04-10'),
(1,  101,  9000, 'debit',  'declined',  '2024-04-15'),
(7,  107, 30000, 'credit', 'approved',  '2024-05-01'),
(7,  107, 15000, 'debit',  'approved',  '2024-05-05'),
(2,  102,  5000, 'credit', 'approved',  '2024-05-10'),
(8,  108,  2000, 'debit',  'approved',  '2024-05-15'),
(1,  101, 11000, 'credit', 'approved',  '2024-05-20');

-- users (for string functions, date, join examples)
CREATE TABLE users (
    id           SERIAL PRIMARY KEY,
    name         VARCHAR(100),
    email        VARCHAR(150),
    phone        VARCHAR(20),
    age          INT,
    gender       CHAR(1),
    city         VARCHAR(100),
    status       VARCHAR(20) DEFAULT 'active',
    created_at   TIMESTAMP DEFAULT NOW(),
    updated_at   TIMESTAMP
);

INSERT INTO users (name, email, phone, age, gender, city, status, created_at) VALUES
('  alice johnson ', 'Alice@LeetCode.com',   '99-88-77-66',   28, 'F', 'Mumbai',    'active',   '2023-01-10 10:00:00'),
('BOB SMITH',        'bob@gmail.com',         '9876543210',    35, 'M', 'Delhi',     'active',   '2023-02-15 11:30:00'),
('Carol White',      'carol@company.com',     '9876543211',    30, 'F', 'Bangalore', 'active',   '2023-03-20 09:00:00'),
('DAVE BROWN',       'dave@yahoo.com',         NULL,           42, 'M', 'Chennai',   'inactive', '2023-04-05 14:00:00'),
('eve davis',        'eve_invalid_email',      '9876543212',   25, 'F', 'Pune',      'active',   '2023-05-12 16:00:00'),
('Frank Miller',     'frank@LeetCode.com',    '98-76-54-32',   31, 'M', 'Hyderabad', 'active',   '2023-06-01 08:00:00'),
('Grace Wilson',     'grace@test.com',         '9876543213',   27, 'F', 'Kolkata',   'active',   '2023-07-18 12:00:00'),
('  Henry Moore  ',  'henry@company.com',      '9876543214',   45, 'M', 'Mumbai',    'inactive', '2023-08-22 15:00:00'),
('Iris Taylor',      'IRIS@LEETCODE.COM',      NULL,           33, 'F', 'Delhi',     'active',   '2023-09-30 10:30:00'),
('Jack Anderson',    'jack@gmail.com',          '9876543215',  38, 'M', 'Bangalore', 'active',   '2023-10-14 09:45:00');

-- events (for JSON, window function, session examples)
CREATE TABLE events (
    id           SERIAL PRIMARY KEY,
    user_id      INT REFERENCES users(id),
    event_type   VARCHAR(50),
    amount       NUMERIC(10,2),
    region       VARCHAR(50),
    event_time   TIMESTAMP,
    data         JSONB
);

INSERT INTO events (user_id, event_type, amount, region, event_time, data) VALUES
(1, 'view',     0,     'North', '2024-01-01 09:00:00', '{"page": "home",    "session": "s001"}'),
(1, 'click',    0,     'North', '2024-01-01 09:05:00', '{"page": "product", "session": "s001"}'),
(1, 'purchase', 75000, 'North', '2024-01-01 09:15:00', '{"product_id": 1,  "session": "s001"}'),
(2, 'view',     0,     'South', '2024-01-02 10:00:00', '{"page": "home",    "session": "s002"}'),
(2, 'click',    0,     'South', '2024-01-02 10:08:00', '{"page": "product", "session": "s002"}'),
(3, 'view',     0,     'East',  '2024-01-03 11:00:00', '{"page": "home",    "session": "s003"}'),
(3, 'purchase', 4500,  'East',  '2024-01-03 11:20:00', '{"product_id": 7,  "session": "s003"}'),
(4, 'view',     0,     'West',  '2024-01-05 14:00:00', '{"page": "sale",    "session": "s004"}'),
(1, 'view',     0,     'North', '2024-02-01 09:00:00', '{"page": "home",    "session": "s005"}'),
(1, 'purchase',12000, 'North',  '2024-02-01 09:30:00', '{"product_id": 3,  "session": "s005"}'),
(5, 'view',     0,     'North', '2024-02-05 15:00:00', '{"page": "product", "session": "s006"}'),
(5, 'purchase', 3500,  'North', '2024-02-05 15:10:00', '{"product_id": 10, "session": "s006"}');

-- ============================================================
-- SECTION 2: WINDOW FUNCTION PRACTICE TABLES
-- Used in: 04_WINDOW_FUNCTIONS.md
-- ============================================================

DROP TABLE IF EXISTS game_scores CASCADE;
DROP TABLE IF EXISTS user_visits CASCADE;
DROP TABLE IF EXISTS daily_revenue CASCADE;

-- game_scores (for running totals, ranking)
CREATE TABLE game_scores (
    id          SERIAL PRIMARY KEY,
    player_id   INT,
    player_name VARCHAR(100),
    score       INT,
    game_date   DATE,
    level       INT
);

INSERT INTO game_scores (player_id, player_name, score, game_date, level) VALUES
(1, 'Alice',  85, '2024-01-01', 1),
(2, 'Bob',    92, '2024-01-01', 1),
(3, 'Carol',  78, '2024-01-01', 1),
(1, 'Alice',  90, '2024-01-02', 2),
(2, 'Bob',    88, '2024-01-02', 2),
(3, 'Carol',  95, '2024-01-02', 2),
(1, 'Alice', 100, '2024-01-03', 3),
(2, 'Bob',    72, '2024-01-03', 3),
(3, 'Carol',  88, '2024-01-03', 3),
(4, 'Dave',   60, '2024-01-01', 1),
(4, 'Dave',   65, '2024-01-02', 2),
(4, 'Dave',   70, '2024-01-03', 3);

-- user_visits (for LAG/LEAD, gap detection)
CREATE TABLE user_visits (
    id          SERIAL PRIMARY KEY,
    user_id     INT,
    visit_date  DATE,
    pages_seen  INT,
    duration    INT  -- minutes
);

INSERT INTO user_visits (user_id, visit_date, pages_seen, duration) VALUES
(1, '2024-01-01', 5,  12),
(1, '2024-01-03', 8,  20),
(1, '2024-01-10', 3,   7),
(1, '2024-01-25', 10, 35),
(2, '2024-01-02', 4,   9),
(2, '2024-01-03', 6,  15),
(2, '2024-01-15', 2,   5),
(3, '2024-01-01', 7,  18),
(3, '2024-01-08', 9,  25),
(3, '2024-01-09', 5,  12),
(3, '2024-02-01', 11, 40),
(4, '2024-01-05', 3,   8),
(4, '2024-01-06', 4,  10),
(4, '2024-01-07', 6,  14);

-- daily_revenue (for time series, rolling averages)
CREATE TABLE daily_revenue (
    id           SERIAL PRIMARY KEY,
    revenue_date DATE,
    amount       NUMERIC(10,2),
    channel      VARCHAR(50)
);

INSERT INTO daily_revenue (revenue_date, amount, channel) VALUES
('2024-01-01',  12000, 'online'),
('2024-01-02',  15000, 'online'),
('2024-01-03',   8000, 'offline'),
('2024-01-04',  20000, 'online'),
('2024-01-05',  18000, 'online'),
('2024-01-06',  22000, 'online'),
('2024-01-07',  25000, 'offline'),
('2024-01-08',  17000, 'online'),
('2024-01-09',  13000, 'online'),
('2024-01-10',  30000, 'online'),
('2024-01-11',  28000, 'online'),
('2024-01-12',  35000, 'online'),
('2024-01-13',  40000, 'offline'),
('2024-01-14',  22000, 'online'),
('2024-01-15',  19000, 'online');

-- ============================================================
-- SECTION 3: LEETCODE TABLES
-- Most-asked LeetCode SQL problems
-- ============================================================

-- ---- Problem #175 Combine Two Tables ----
DROP TABLE IF EXISTS Address CASCADE;
DROP TABLE IF EXISTS Person CASCADE;

CREATE TABLE Person (personId INT PRIMARY KEY, firstName VARCHAR(50), lastName VARCHAR(50));
CREATE TABLE Address (addressId INT PRIMARY KEY, personId INT, city VARCHAR(50), state VARCHAR(50));

INSERT INTO Person VALUES (1,'Wang','Allen'), (2,'Alice','Bob'), (3,'John','Doe');
INSERT INTO Address VALUES (1,2,'New York','New York'), (2,3,'Leetcode','California');

-- ---- Problem #181 Employees Earning More Than Manager ----
DROP TABLE IF EXISTS Employee CASCADE;
CREATE TABLE Employee (id INT PRIMARY KEY, name VARCHAR(50), salary INT, managerId INT);

INSERT INTO Employee VALUES
(1,'Joe',   70000, 3),
(2,'Henry', 80000, 4),
(3,'Sam',   60000, NULL),
(4,'Max',   90000, NULL),
(5,'Janet', 69000, 3),
(6,'Randy', 85000, 4);

-- ---- Problem #182 Duplicate Emails & #196 Delete Duplicates ----
DROP TABLE IF EXISTS emails_table CASCADE;
CREATE TABLE emails_table (id INT PRIMARY KEY, email VARCHAR(100));

INSERT INTO emails_table VALUES
(1, 'a@b.com'),
(2, 'c@d.com'),
(3, 'a@b.com'),
(4, 'e@f.com'),
(5, 'c@d.com');

-- ---- Problem #183 Customers Who Never Order ----
DROP TABLE IF EXISTS CustomerOrders CASCADE;
DROP TABLE IF EXISTS CustomerList CASCADE;

CREATE TABLE CustomerList (id INT PRIMARY KEY, name VARCHAR(50));
CREATE TABLE CustomerOrders (id INT PRIMARY KEY, customerId INT);

INSERT INTO CustomerList VALUES (1,'Joe'),(2,'Henry'),(3,'Sam'),(4,'Max');
INSERT INTO CustomerOrders VALUES (1,3),(2,1);

-- ---- Problem #177 / #178 Salary Ranking ----
DROP TABLE IF EXISTS Salaries CASCADE;
CREATE TABLE Salaries (id INT PRIMARY KEY, salary INT);

INSERT INTO Salaries VALUES
(1, 100),(2, 200),(3, 300),(4, 200),(5, 100),(6, 400),(7, 300);

-- ---- Problem #180 Consecutive Numbers ----
DROP TABLE IF EXISTS Logs CASCADE;
CREATE TABLE Logs (id INT PRIMARY KEY, num INT);

INSERT INTO Logs VALUES
(1,1),(2,1),(3,1),(4,2),(5,1),(6,2),(7,2),(8,3),(9,3),(10,3),(11,3);

-- ---- Problem #184 / #185 Department Salaries ----
DROP TABLE IF EXISTS Dept CASCADE;
DROP TABLE IF EXISTS EmpDept CASCADE;

CREATE TABLE Dept (id INT PRIMARY KEY, name VARCHAR(50));
CREATE TABLE EmpDept (id INT PRIMARY KEY, name VARCHAR(50), salary INT, departmentId INT);

INSERT INTO Dept VALUES (1,'IT'),(2,'Sales'),(3,'Finance');
INSERT INTO EmpDept VALUES
(1,'Joe',   85000, 1),
(2,'Henry', 80000, 2),
(3,'Sam',   60000, 2),
(4,'Max',   90000, 1),
(5,'Janet', 69000, 1),
(6,'Randy', 85000, 1),
(7,'Will',  70000, 1),
(8,'Anna',  75000, 2),
(9,'Tom',   60000, 3),
(10,'Eve',  95000, 3);

-- ---- Problem #197 Rising Temperature ----
DROP TABLE IF EXISTS Weather CASCADE;
CREATE TABLE Weather (id INT PRIMARY KEY, recordDate DATE, temperature INT);

INSERT INTO Weather VALUES
(1,'2015-01-01',10),
(2,'2015-01-02',25),
(3,'2015-01-03',20),
(4,'2015-01-04',30),
(5,'2015-01-05',28),
(6,'2015-01-06',35),
(7,'2015-01-07',32),
(8,'2015-01-08',40);

-- ---- Problem #595 Big Countries ----
DROP TABLE IF EXISTS World CASCADE;
CREATE TABLE World (name VARCHAR(100), continent VARCHAR(50), area INT, population INT, gdp BIGINT);

INSERT INTO World VALUES
('Afghanistan', 'Asia',       652230,  25500100,  20343000000),
('Albania',     'Europe',      28748,   2831741,  12960000000),
('Algeria',     'Africa',    2381741,  37100000, 188681000000),
('Andorra',     'Europe',        468,    78115,   3712000000),
('Angola',      'Africa',    1246700,  20609294, 100990000000),
('China',       'Asia',      9596960,1366686100,11015442000000),
('India',       'Asia',      3287263,1295291543,  2048517000000),
('Brazil',      'Americas',  8515767, 202794000,  2245673000000);

-- ---- Problem #596 Classes With 5+ Students ----
DROP TABLE IF EXISTS Courses CASCADE;
CREATE TABLE Courses (student VARCHAR(50), class VARCHAR(50));

INSERT INTO Courses VALUES
('A','Math'),('B','English'),('C','Math'),('D','Biology'),
('E','Math'), ('F','Computer'),('G','Math'),('H','English'),
('I','Math'), ('J','English'),('K','English'),('L','English'),
('M','English'),('N','Computer');

-- ---- Problem #620 Not Boring Movies ----
DROP TABLE IF EXISTS Cinema CASCADE;
CREATE TABLE Cinema (id INT PRIMARY KEY, movie VARCHAR(100), description VARCHAR(100), rating DECIMAL(3,1));

INSERT INTO Cinema VALUES
(1,'War',    'great 3D',  8.9),
(2,'Science','fiction',   8.5),
(3,'irish',  'boring',    6.2),
(4,'Ice song','Fantacy',  8.6),
(5,'House card','Interesting', 9.1),
(6,'Night',  'dark',      7.0),
(7,'Avengers','superhero',9.0);

-- ---- Problem #1050 ActorDirector ----
DROP TABLE IF EXISTS ActorDirector CASCADE;
CREATE TABLE ActorDirector (actor_id INT, director_id INT, timestamp INT);

INSERT INTO ActorDirector VALUES
(1,1,0),(1,1,1),(1,1,2),
(1,2,3),(1,2,4),
(2,1,5),(2,1,6),(2,1,7),(2,1,8);

-- ---- Problem #1068/1069 Product Sales Analysis ----
DROP TABLE IF EXISTS ProductList CASCADE;
DROP TABLE IF EXISTS SalesList CASCADE;

CREATE TABLE ProductList (product_id INT PRIMARY KEY, product_name VARCHAR(100));
CREATE TABLE SalesList (sale_id INT PRIMARY KEY, product_id INT, year INT, quantity INT, price INT);

INSERT INTO ProductList VALUES (100,'Nokia'),(200,'Apple'),(300,'Samsung');
INSERT INTO SalesList VALUES
(1,100,2008,10,5000),
(2,100,2009,12,5000),
(3,200,2011,15,9000),
(7,200,2012,8,9000);

-- ---- Problem #1141 / #1142 User Activity ----
DROP TABLE IF EXISTS Activity CASCADE;
CREATE TABLE Activity (
    user_id INT, session_id INT, activity_date DATE, activity_type VARCHAR(50)
);

INSERT INTO Activity VALUES
(1,1,'2019-07-20','open_session'),
(1,1,'2019-07-20','scroll_down'),
(1,1,'2019-07-20','end_session'),
(2,4,'2019-07-20','open_session'),
(2,4,'2019-07-21','send_message'),
(2,4,'2019-07-21','end_session'),
(3,2,'2019-07-21','open_session'),
(3,2,'2019-07-21','send_message'),
(3,2,'2019-07-21','end_session'),
(4,3,'2019-06-25','open_session'),
(4,3,'2019-06-25','end_session');

-- ---- Problem #1148 / #1149 Article Views ----
DROP TABLE IF EXISTS Views CASCADE;
CREATE TABLE Views (article_id INT, author_id INT, viewer_id INT, view_date DATE);

INSERT INTO Views VALUES
(1,3,5,'2019-08-01'),
(1,3,6,'2019-08-02'),
(2,7,7,'2019-08-01'),
(2,7,6,'2019-08-02'),
(4,7,1,'2019-07-22'),
(3,4,4,'2019-07-21'),
(3,4,4,'2019-07-21');

-- ---- Problem #1158 Market Analysis ----
DROP TABLE IF EXISTS Buyers CASCADE;
DROP TABLE IF EXISTS OrderItems CASCADE;

CREATE TABLE Buyers (buyer_id INT PRIMARY KEY, join_date DATE);
CREATE TABLE OrderItems (order_id INT PRIMARY KEY, order_date DATE, item_id INT, buyer_id INT, seller_id INT);

INSERT INTO Buyers VALUES (1,'2018-01-01'),(2,'2018-02-09'),(3,'2018-01-19'),(4,'2018-05-21');
INSERT INTO OrderItems VALUES
(1,'2019-08-01',4,1,2),
(2,'2018-08-02',2,1,3),
(3,'2019-08-15',3,2,3),
(4,'2018-09-05',1,2,2);

-- ---- Problem #1173 / #1174 Delivery ----
DROP TABLE IF EXISTS Delivery CASCADE;
CREATE TABLE Delivery (
    delivery_id INT PRIMARY KEY,
    customer_id INT,
    order_date DATE,
    customer_pref_delivery_date DATE
);

INSERT INTO Delivery VALUES
(1,1,'2019-08-01','2019-08-02'),
(2,5,'2019-08-02','2019-08-02'),
(3,1,'2019-08-11','2019-08-11'),
(4,3,'2019-08-24','2019-08-26'),
(5,4,'2019-08-21','2019-08-22'),
(6,2,'2019-08-11','2019-08-13'),
(7,4,'2019-08-09','2019-08-09');

-- ---- Problem #1179 Reformat Department Table ----
DROP TABLE IF EXISTS DeptRevenue CASCADE;
CREATE TABLE DeptRevenue (id INT, revenue INT, month VARCHAR(5));

INSERT INTO DeptRevenue VALUES
(1,8000,'Jan'),(2,9000,'Jan'),(3,10000,'Feb'),
(1,7000,'Feb'),(1,6000,'Mar'),(2,6000,'Apr');

-- ---- Problem #1193 Monthly Transactions ----
DROP TABLE IF EXISTS MonthlyTransactions CASCADE;
CREATE TABLE MonthlyTransactions (
    id INT PRIMARY KEY, country VARCHAR(50), state VARCHAR(20), amount INT, trans_date DATE
);

INSERT INTO MonthlyTransactions VALUES
(121,'US',     'approved', 1000,'2018-12-18'),
(122,'US',     'declined', 2000,'2018-12-19'),
(123,'US',     'approved',2000, '2019-01-01'),
(124,'DE',     'approved',2000, '2019-01-07');

-- ---- Problem #1211 Queries Quality ----
DROP TABLE IF EXISTS Queries CASCADE;
CREATE TABLE Queries (query_name VARCHAR(50), result VARCHAR(100), position INT, rating INT);

INSERT INTO Queries VALUES
('Dog','Golden Retriever',1,5),('Dog','German Shepherd',2,5),
('Dog','Mule',200,1),('Cat','Shirazi',5,2),
('Cat','Siamese',3,3),('Cat','Sphynx',7,4);

-- ---- Problem #1251 Weighted Average Price ----
DROP TABLE IF EXISTS Prices CASCADE;
DROP TABLE IF EXISTS UnitsSold CASCADE;

CREATE TABLE Prices (product_id INT, start_date DATE, end_date DATE, price INT);
CREATE TABLE UnitsSold (product_id INT, purchase_date DATE, units INT);

INSERT INTO Prices VALUES
(1,'2019-02-17','2019-02-28',5),
(1,'2019-03-01','2019-03-22',20),
(2,'2019-02-01','2019-02-20',15),
(2,'2019-02-21','2019-03-31',30);

INSERT INTO UnitsSold VALUES
(1,'2019-02-25',100),
(1,'2019-03-01',15),
(2,'2019-02-10',200),
(2,'2019-03-22',30);

-- ---- Problem #1280 Students and Examinations ----
DROP TABLE IF EXISTS Examinations CASCADE;
DROP TABLE IF EXISTS Students CASCADE;
DROP TABLE IF EXISTS Subjects CASCADE;

CREATE TABLE Students  (student_id INT, student_name VARCHAR(50));
CREATE TABLE Subjects  (subject_name VARCHAR(50));
CREATE TABLE Examinations (student_id INT, subject_name VARCHAR(50));

INSERT INTO Students  VALUES (1,'Alice'),(2,'Bob'),(13,'John'),(6,'Alex');
INSERT INTO Subjects  VALUES ('Math'),('Physics'),('Programming');
INSERT INTO Examinations VALUES
(1,'Math'),(1,'Physics'),(1,'Programming'),
(2,'Programming'),
(1,'Physics'),(1,'Math'),
(13,'Math'),(13,'Programming'),
(13,'Physics'),(6,'Math'),(6,'Physics');

-- ---- Problem #1321 Restaurant Growth (Rolling 7-day avg) ----
DROP TABLE IF EXISTS Restaurant CASCADE;
CREATE TABLE Restaurant (customer_id INT, name VARCHAR(50), visited_on DATE, amount INT);

INSERT INTO Restaurant VALUES
(1,'Jhon',   '2019-01-01',100),
(2,'Daniel', '2019-01-02',110),
(3,'Jade',   '2019-01-03',120),
(4,'Khaled', '2019-01-04',130),
(5,'Winston','2019-01-05',110),
(6,'Elvis',  '2019-01-06',140),
(7,'Anna',   '2019-01-07',150),
(8,'Maria',  '2019-01-08',80),
(9,'Jaze',   '2019-01-09',110),
(1,'Jhon',   '2019-01-10',130),
(3,'Jade',   '2019-01-10',150);

-- ---- Problem #1378 Replace Employee ID ----
DROP TABLE IF EXISTS EmployeeUNI CASCADE;
DROP TABLE IF EXISTS EmployeeInfo CASCADE;

CREATE TABLE EmployeeInfo (id INT PRIMARY KEY, name VARCHAR(50));
CREATE TABLE EmployeeUNI (id INT, unique_id INT);

INSERT INTO EmployeeInfo VALUES (1,'Alice'),(7,'Bob'),(11,'Meir'),(90,'Winston'),(3,'Jonathan');
INSERT INTO EmployeeUNI VALUES (3,1),(11,2),(90,3);

-- ---- Problem #1393 Capital Gain/Loss ----
DROP TABLE IF EXISTS Stocks CASCADE;
CREATE TABLE Stocks (stock_name VARCHAR(50), operation VARCHAR(10), operation_day INT, price INT);

INSERT INTO Stocks VALUES
('Leetcode',    'Buy',  1, 1000),
('Corona Masks','Buy',  2, 10),
('Leetcode',    'Sell', 5, 9000),
('Handbags',    'Buy',  17,30000),
('Corona Masks','Sell', 3, 1010),
('Corona Masks','Buy',  4, 1000),
('Corona Masks','Sell', 5, 500),
('Corona Masks','Buy',  6, 1000),
('Handbags',    'Sell', 29,7000),
('Corona Masks','Sell', 10,10000);

-- ---- Problem #1407 Top Travellers ----
DROP TABLE IF EXISTS Rides CASCADE;
DROP TABLE IF EXISTS Travellers CASCADE;

CREATE TABLE Travellers (id INT PRIMARY KEY, name VARCHAR(50));
CREATE TABLE Rides (id INT PRIMARY KEY, user_id INT, distance INT);

INSERT INTO Travellers VALUES (1,'Alice'),(2,'Bob'),(3,'Alex'),(4,'Donald'),(7,'Lee'),(13,'Jonathan'),(19,'Elvis');
INSERT INTO Rides VALUES
(1,1,120),(2,2,317),(3,3,222),(4,7,100),(5,13,312),(6,19,50),(7,7,120),(8,19,400),(9,7,230);

-- ---- Problem #1484 Group Sold Products ----
DROP TABLE IF EXISTS Activities CASCADE;
CREATE TABLE Activities (sell_date DATE, product VARCHAR(50));

INSERT INTO Activities VALUES
('2020-05-30','Headphone'),
('2020-06-01','Pencil'),
('2020-06-02','Mask'),
('2020-05-30','Basketball'),
('2020-06-01','Bible'),
('2020-06-02','Mask'),
('2020-05-30','T-Shirt');

-- ---- Problem #1527 Patients With Condition ----
DROP TABLE IF EXISTS Patients CASCADE;
CREATE TABLE Patients (patient_id INT PRIMARY KEY, patient_name VARCHAR(50), conditions VARCHAR(200));

INSERT INTO Patients VALUES
(1,'Daniel',  'YFEV COUGH'),
(2,'Alice',   ''),
(3,'Bob',     'DIAB100 MYOP'),
(4,'George',  'ACNE DIAB100'),
(5,'Alain',   'DIAB201'),
(6,'Jayden',  'DIAB1'),
(7,'Smith',   'MYOP DIAB1 YFEV');

-- ---- Problem #1633 / #1934 Confirmation Rate ----
DROP TABLE IF EXISTS Confirmations CASCADE;
DROP TABLE IF EXISTS Signups CASCADE;

CREATE TABLE Signups (user_id INT PRIMARY KEY, time_stamp TIMESTAMP);
CREATE TABLE Confirmations (user_id INT, time_stamp TIMESTAMP, action VARCHAR(20));

INSERT INTO Signups VALUES
(3,'2020-03-21 10:16:13'),
(7,'2020-01-04 13:57:59'),
(2,'2020-07-29 23:09:44'),
(6,'2020-12-09 10:39:37');

INSERT INTO Confirmations VALUES
(3,'2021-01-06 03:30:46','timeout'),
(3,'2021-07-14 14:00:00','timeout'),
(7,'2021-06-12 11:57:29','confirmed'),
(7,'2021-06-13 12:58:28','confirmed'),
(7,'2021-06-14 13:59:27','confirmed'),
(2,'2021-01-22 00:00:00','confirmed'),
(2,'2021-02-28 23:59:59','timeout');

-- ---- Problem #1667 Fix Names ----
DROP TABLE IF EXISTS UserNames CASCADE;
CREATE TABLE UserNames (user_id INT PRIMARY KEY, name VARCHAR(50));

INSERT INTO UserNames VALUES
(1,'aLice'),(2,'bOB'),(3,'CAROL'),(4,'dave'),(5,'EVE');

-- ---- Problem #1731 Employees Reporting ----
DROP TABLE IF EXISTS ReportingTree CASCADE;
CREATE TABLE ReportingTree (employee_id INT PRIMARY KEY, name VARCHAR(50), reports_to INT, age INT);

INSERT INTO ReportingTree VALUES
(9,'Hercy',  NULL, 43),
(6,'Alice',  9,    41),
(4,'Bob',    9,    36),
(2,'Winston',NULL, 37);

-- ---- Problem #1757 Recyclable Low Fat ----
DROP TABLE IF EXISTS ProductFlags CASCADE;
CREATE TABLE ProductFlags (product_id INT PRIMARY KEY, low_fats CHAR(1), recyclable CHAR(1));

INSERT INTO ProductFlags VALUES
(0,'Y','N'),(1,'Y','Y'),(2,'N','Y'),(3,'Y','Y'),(4,'N','N');

-- ---- Problem #1873 Special Bonus ----
DROP TABLE IF EXISTS EmpBonus CASCADE;
CREATE TABLE EmpBonus (employee_id INT PRIMARY KEY, name VARCHAR(50), salary INT);

INSERT INTO EmpBonus VALUES
(2,'Meir',   3000),
(3,'Michael',3800),
(7,'Addilyn',7400),
(8,'Juan',   6100),
(9,'Kana',   7700);

-- ---- Problem #1890 Latest Login ----
DROP TABLE IF EXISTS Logins CASCADE;
CREATE TABLE Logins (user_id INT, time_stamp TIMESTAMP);

INSERT INTO Logins VALUES
(6, '2020-06-30 15:14:22'),
(1, '2020-02-01 09:00:00'),
(6, '2021-04-21 14:06:06'),
(6, '2019-03-07 00:18:15'),
(8, '2020-02-01 05:10:53'),
(1, '2020-12-07 23:20:50'),
(2, '2020-01-16 02:49:50'),
(2, '2020-01-16 02:49:50');

-- ---- Problem #1907 Count Salary Categories ----
DROP TABLE IF EXISTS Accounts CASCADE;
CREATE TABLE Accounts (account_id INT PRIMARY KEY, income INT);

INSERT INTO Accounts VALUES
(3,108939),(2,12747),(8,87709),(6,91796);

-- ---- Problem #610 Triangle Judgement ----
DROP TABLE IF EXISTS Triangle CASCADE;
CREATE TABLE Triangle (x INT, y INT, z INT);

INSERT INTO Triangle VALUES (13,15,30),(10,20,15),(3,4,5),(1,1,1);

-- ---- Problem #626 Exchange Seats ----
DROP TABLE IF EXISTS Seat CASCADE;
CREATE TABLE Seat (id INT PRIMARY KEY, student VARCHAR(50));

INSERT INTO Seat VALUES (1,'Abbot'),(2,'Doris'),(3,'Emerson'),(4,'Green'),(5,'Jeames');

-- ---- Problem #627 Swap Sex ----
DROP TABLE IF EXISTS SalaryGender CASCADE;
CREATE TABLE SalaryGender (id INT PRIMARY KEY, name VARCHAR(50), sex CHAR(1), salary INT);

INSERT INTO SalaryGender VALUES
(1,'A','m',2500),(2,'B','f',1500),(3,'C','m',5500),(4,'D','f',500);

-- ---- Tree Node (classify root/inner/leaf) ----
DROP TABLE IF EXISTS Tree CASCADE;
CREATE TABLE Tree (id INT PRIMARY KEY, p_id INT);

INSERT INTO Tree VALUES (1,NULL),(2,1),(3,1),(4,2),(5,2);

-- ---- Problem #1204 Last Person to Fit in Bus ----
DROP TABLE IF EXISTS Queue CASCADE;
CREATE TABLE Queue (person_id INT PRIMARY KEY, person_name VARCHAR(50), weight INT, turn INT);

INSERT INTO Queue VALUES
(5,'Alice', 250,1),(4,'Bob',  175,5),(3,'Alex', 350,2),
(6,'John',  400,3),(1,'Winston',500,6),(2,'Marie',200,4);

-- ============================================================
-- SECTION 4: ADVANCED PATTERNS TABLES
-- Used in: 12_ADVANCED_PATTERNS.md
-- ============================================================

DROP TABLE IF EXISTS failed_days CASCADE;
DROP TABLE IF EXISTS succeeded_days CASCADE;
DROP TABLE IF EXISTS user_activity CASCADE;
DROP TABLE IF EXISTS api_logs CASCADE;

-- failed_days / succeeded_days (contiguous dates)
CREATE TABLE failed_days    (fail_date    DATE);
CREATE TABLE succeeded_days (success_date DATE);

INSERT INTO failed_days    VALUES ('2019-01-01'),('2019-01-02'),('2019-01-04'),('2019-01-05');
INSERT INTO succeeded_days VALUES ('2019-01-03'),('2019-01-06'),('2019-01-07');

-- user_activity (retention, churn)
CREATE TABLE user_activity (
    id          SERIAL PRIMARY KEY,
    user_id     INT,
    event_type  VARCHAR(50),
    activity_date DATE
);

INSERT INTO user_activity (user_id, event_type, activity_date) VALUES
(1, 'login',    '2024-01-01'),
(1, 'purchase', '2024-01-05'),
(1, 'login',    '2024-01-10'),
(2, 'login',    '2024-01-02'),
(2, 'login',    '2024-01-03'),
(3, 'login',    '2024-01-01'),
(3, 'purchase', '2024-01-15'),
(3, 'login',    '2024-02-01'),
(4, 'login',    '2024-01-01'),
-- user 4 inactive since Jan — potential churn
(5, 'login',    '2024-01-01'),
(5, 'login',    '2024-01-02'),
(5, 'purchase', '2024-01-03'),
(5, 'login',    '2024-04-01');  -- came back after long gap

-- api_logs (for performance analysis)
CREATE TABLE api_logs (
    id             SERIAL PRIMARY KEY,
    endpoint       VARCHAR(100),
    response_time  INT,   -- milliseconds
    status_code    INT,
    logged_at      TIMESTAMP
);

INSERT INTO api_logs (endpoint, response_time, status_code, logged_at) VALUES
('/api/users',    120, 200, '2024-01-01 10:00:01'),
('/api/orders',   350, 200, '2024-01-01 10:00:05'),
('/api/products', 80,  200, '2024-01-01 10:00:10'),
('/api/users',    0,   500, '2024-01-01 10:01:00'),
('/api/orders',   450, 200, '2024-01-01 10:05:00'),
('/api/products', 95,  200, '2024-01-01 10:10:00'),
('/api/users',    110, 200, '2024-01-01 11:00:00'),
('/api/orders',   380, 404, '2024-01-01 11:30:00'),
('/api/products', 90,  200, '2024-01-01 12:00:00'),
('/api/users',    130, 200, '2024-01-01 12:30:00');

-- ============================================================
-- SECTION 5: STRING FUNCTION TABLES
-- Used in: 07_STRING_FUNCTIONS.md
-- ============================================================

DROP TABLE IF EXISTS contacts CASCADE;
DROP TABLE IF EXISTS raw_products CASCADE;

CREATE TABLE contacts (
    id       SERIAL PRIMARY KEY,
    name     VARCHAR(100),
    email    VARCHAR(150),
    phone    VARCHAR(30),
    address  VARCHAR(200)
);

INSERT INTO contacts (name, email, phone, address) VALUES
('  Alice Johnson  ',  'alice@company.com',      '+91-98-765-43210',   '12, MG Road, Mumbai'),
('BOB SMITH',          'bob@gmail.com',           '(98) 76543211',     '34 Park Street, Delhi'),
('carol white',        'carol@invalid',            '9876-54-3212',      '56 Lake View, Bangalore'),
('DAVE BROWN',         'dave_at_yahoo_dot_com',    '98765.43213',       '78 Hill Top, Chennai'),
('  eve davis  ',      'eve@LeetCode.com',         '+919876543214',     '90 Sea Face, Mumbai');

CREATE TABLE raw_products (
    id           SERIAL PRIMARY KEY,
    product_name VARCHAR(150),
    sale_date    VARCHAR(20),
    cnt          INT
);

INSERT INTO raw_products (product_name, sale_date, cnt) VALUES
('  PHONE  ',      '2020-12-01', 10),
('phone',          '2020-12-01', 5),
(' Keyboard ',     '2020-12-02', 3),
('KEYBOARD',       '2020-12-02', 7),
('Mouse',          '2020-12-03', 8),
('  mouse  ',      '2020-12-03', 4);

-- ============================================================
-- SECTION 6: JSON / ARRAY TABLES (PostgreSQL specific)
-- Used in: 14_ARRAY_JSON_FUNCTIONS.md
-- ============================================================

DROP TABLE IF EXISTS json_events CASCADE;
DROP TABLE IF EXISTS product_tags CASCADE;

CREATE TABLE json_events (
    id      SERIAL PRIMARY KEY,
    user_id INT,
    data    JSONB
);

INSERT INTO json_events (user_id, data) VALUES
(1, '{"event": "purchase", "amount": 75000, "product_id": 1, "tags": ["electronics","laptop"], "address": {"city": "Mumbai", "pin": "400001"}}'),
(2, '{"event": "view",     "amount": 0,     "product_id": 2, "tags": ["electronics"],           "address": {"city": "Delhi",  "pin": "110001"}}'),
(3, '{"event": "purchase", "amount": 4500,  "product_id": 7, "tags": ["electronics","keyboard"],"address": {"city": "Bangalore","pin":"560001"}}'),
(1, '{"event": "purchase", "amount": 12000, "product_id": 3, "tags": ["furniture","chair"],      "address": {"city": "Mumbai", "pin": "400001"}}'),
(4, '{"event": "cart",     "amount": 3500,  "product_id": 10,"tags": ["electronics","webcam"],   "address": {"city": "Chennai","pin": "600001"}}');

CREATE TABLE product_tags (
    id       SERIAL PRIMARY KEY,
    name     VARCHAR(100),
    category VARCHAR(50),
    tags     TEXT[]
);

INSERT INTO product_tags (name, category, tags) VALUES
('Laptop Pro 15',       'Electronics',  ARRAY['premium','laptop','portable','lightweight']),
('Wireless Mouse',      'Electronics',  ARRAY['wireless','mouse','ergonomic']),
('Office Chair',        'Furniture',    ARRAY['ergonomic','office','adjustable']),
('Python Book',         'Books',        ARRAY['python','programming','beginner']),
('SQL Guide',           'Books',        ARRAY['sql','database','intermediate']),
('Mechanical Keyboard', 'Electronics',  ARRAY['mechanical','keyboard','gaming','rgb']),
('Standing Desk',       'Furniture',    ARRAY['standing','desk','adjustable','ergonomic']);

-- ============================================================
-- SECTION 7: QUICK VERIFICATION QUERIES
-- Run these to confirm all tables loaded correctly
-- ============================================================

-- SELECT 'employees'    AS tbl, COUNT(*) AS rows FROM employees
-- UNION ALL SELECT 'departments', COUNT(*) FROM departments
-- UNION ALL SELECT 'customers',   COUNT(*) FROM customers
-- UNION ALL SELECT 'products',    COUNT(*) FROM products
-- UNION ALL SELECT 'orders',      COUNT(*) FROM orders
-- UNION ALL SELECT 'sales',       COUNT(*) FROM sales
-- UNION ALL SELECT 'transactions',COUNT(*) FROM transactions
-- UNION ALL SELECT 'users',       COUNT(*) FROM users
-- UNION ALL SELECT 'events',      COUNT(*) FROM events
-- UNION ALL SELECT 'Weather',     COUNT(*) FROM Weather
-- UNION ALL SELECT 'Logs',        COUNT(*) FROM Logs
-- UNION ALL SELECT 'Employee',    COUNT(*) FROM Employee
-- UNION ALL SELECT 'Activity',    COUNT(*) FROM Activity
-- ORDER BY tbl;

-- ============================================================
-- END OF SETUP
-- ============================================================
