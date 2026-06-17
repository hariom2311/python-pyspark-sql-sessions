# Day 2 — SQL: String Functions

> **Roadmap Day:** 2 · **Date:** Tuesday, June 16, 2026  
> **Study Window:** 9 PM – 11 PM  
> **Dataset:** `customers(customer_id, full_name, email, phone, address)`

---

## 1. The Dataset

```sql
CREATE TABLE customers (
    customer_id  INT PRIMARY KEY,
    full_name    VARCHAR(100),
    email        VARCHAR(150),
    phone        VARCHAR(30),
    address      VARCHAR(200)
);

INSERT INTO customers VALUES
(1,  '  Alice Johnson  ',  'ALICE@Gmail.COM   ', '  +91-98765-43210 ', '12, MG Road, Mumbai'),
(2,  'bob smith',           'bob@yahoo.com',      '9876100002',         '45 Park Street, Delhi'),
(3,  'CAROL WHITE',         ' carol@hotmail.com', '(098) 761-00003',    '7/B Lake View, Chennai'),
(4,  'David Brown',         'david@gmail.com',    '987.610.0004',       '22 Hill Top, Pune'),
(5,  'eve nair  ',          'EVE@GMAIL.COM',      '+919876100005',      '8 MG Road, Bangalore'),
(6,  'Frank Singh',         'frank@outlook.com',  '98-7610-0006',       '33 Nehru Place, Hyderabad'),
(7,  'GRACE PATEL',         'GRACE@yahoo.com ',   '9876100007',         '15 Ring Road, Kolkata'),
(8,  '  henry das',         'henry@gmail.com',    '(987) 610-0008',     '9 Carter Road, Ahmedabad'),
(9,  'Irene Verma',         'irene@gmail.COM',    '9876100009  ',       '5 Civil Lines, Jaipur'),
(10, 'jack KUMAR',          'JACK@hotmail.com',   '987-610-0010',       '18 Anna Nagar, Surat');
```

Notice the intentional mess: mixed case, leading/trailing spaces, varied phone formats. This is real-world data quality work.

---

## 2. UPPER / LOWER — Case Standardisation

```sql
-- Standardise email to lowercase
SELECT
    customer_id,
    email,
    LOWER(email) AS email_clean
FROM customers;

-- Standardise name to title case (PostgreSQL uses initcap)
SELECT
    full_name,
    INITCAP(TRIM(full_name)) AS name_clean
FROM customers;

-- UPPER — useful for case-insensitive comparison
SELECT * FROM customers
WHERE UPPER(TRIM(email)) = 'ALICE@GMAIL.COM';
```

---

## 3. TRIM / LTRIM / RTRIM — Whitespace Removal

```sql
-- TRIM removes both leading and trailing whitespace
SELECT
    customer_id,
    TRIM(full_name)  AS name_trimmed,
    TRIM(email)      AS email_trimmed,
    TRIM(phone)      AS phone_trimmed
FROM customers;

-- LTRIM — left (leading) only
SELECT LTRIM('   hello   ');   -- 'hello   '

-- RTRIM — right (trailing) only
SELECT RTRIM('   hello   ');   -- '   hello'

-- TRIM(BOTH '.' FROM str) — trim a specific character
SELECT TRIM(BOTH '+91' FROM '+919876543210');
-- Careful: TRIM removes characters, not substrings — removes any +, 9, 1 from both ends
```

**Best practice:** Always `TRIM` before `LOWER` before comparison:
```sql
WHERE TRIM(LOWER(email)) = 'alice@gmail.com'
```

---

## 4. REPLACE — Substitute Characters or Substrings

```sql
-- Clean phone: remove dashes, spaces, parens, dots
SELECT
    phone,
    REPLACE(
        REPLACE(
            REPLACE(
                REPLACE(
                    REPLACE(TRIM(phone), '-', ''),
                    ' ', ''),
                '(', ''),
            ')', ''),
        '.', '') AS phone_digits_only
FROM customers;
```

**Pattern:** Nest `REPLACE()` calls — each strips one unwanted character.

---

## 5. SUBSTRING / SUBSTR — Extract Part of a String

```sql
-- SUBSTRING(string FROM start FOR length)   ← SQL standard
-- SUBSTR(string, start, length)             ← shorthand, same behaviour in PostgreSQL

-- Extract year from a date-string column
SELECT SUBSTRING('2024-01-15' FROM 1 FOR 4);  -- '2024'
SELECT SUBSTRING('2024-01-15' FROM 6 FOR 2);  -- '01'  (month)
SELECT SUBSTRING('2024-01-15' FROM 9 FOR 2);  -- '15'  (day)

-- Extract domain from email
SELECT
    email,
    SUBSTRING(email FROM POSITION('@' IN email) + 1) AS domain
FROM customers;

-- SPLIT_PART(string, delimiter, field_number)  ← PostgreSQL-specific, very handy
SELECT
    full_name,
    SPLIT_PART(TRIM(full_name), ' ', 1) AS first_name,
    SPLIT_PART(TRIM(full_name), ' ', 2) AS last_name
FROM customers;
```

---

## 6. CONCAT / || — Combine Strings

```sql
-- CONCAT — null-safe concatenation (nulls become empty string)
SELECT CONCAT(first_name, ' ', last_name) AS full_name;

-- || operator — null propagates (if any part is NULL, result is NULL)
SELECT first_name || ' ' || last_name AS full_name;

-- CONCAT_WS(separator, val1, val2, ...) — concat with separator, skips NULLs
SELECT CONCAT_WS(', ', city, state, country) AS full_address;

-- Build a display label
SELECT
    customer_id,
    CONCAT(INITCAP(TRIM(full_name)), ' <', LOWER(TRIM(email)), '>') AS display_label
FROM customers;
-- Example: Alice Johnson <alice@gmail.com>
```

---

## 7. LENGTH / CHAR_LENGTH — String Length

```sql
-- LENGTH and CHAR_LENGTH are equivalent for standard text in PostgreSQL
SELECT
    phone,
    LENGTH(TRIM(phone))       AS raw_length,
    LENGTH(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
        TRIM(phone), '-',''), ' ',''), '(',''), ')',''), '.',''))
        AS digits_length
FROM customers;

-- Find rows where cleaned phone doesn't have 10 digits
SELECT customer_id, full_name, phone
FROM customers
WHERE LENGTH(
    REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
        TRIM(phone), '-',''), ' ',''), '(',''), ')',''), '.','')
) != 10;
```

---

## 8. POSITION / STRPOS — Find Substring Location

```sql
-- POSITION(substring IN string) — returns 1-based index, 0 if not found
SELECT POSITION('@' IN 'alice@gmail.com');   -- 6

-- STRPOS(string, substring) — same, different syntax
SELECT STRPOS('alice@gmail.com', '@');       -- 6

-- Use to validate email format
SELECT
    customer_id,
    email,
    CASE WHEN POSITION('@' IN TRIM(email)) > 0 THEN 'valid' ELSE 'invalid' END AS email_check
FROM customers;
```

---

## 9. REGEXP_REPLACE — Pattern-Based Replacement

```sql
-- Remove all non-digit characters from phone using regex
SELECT
    phone,
    REGEXP_REPLACE(TRIM(phone), '[^0-9]', '', 'g') AS phone_clean
FROM customers;
-- 'g' flag = global (replace all matches, not just first)

-- Remove all whitespace
SELECT REGEXP_REPLACE('  hello   world  ', '\s+', ' ', 'g');  -- ' hello world '
SELECT TRIM(REGEXP_REPLACE('  hello   world  ', '\s+', ' ', 'g'));  -- 'hello world'
```

**`REGEXP_REPLACE(string, pattern, replacement, flags)`**
- Pattern uses standard regex
- `'g'` flag replaces all occurrences
- `'i'` flag is case-insensitive

---

## 10. Day 2 Problems — Solutions

### Problem 1 (Easy) — Standardise emails
```sql
SELECT
    customer_id,
    TRIM(LOWER(email)) AS email_clean
FROM customers
ORDER BY customer_id;
```

### Problem 2 (Easy) — Split full_name into first and last
```sql
SELECT
    customer_id,
    TRIM(full_name)                          AS full_name,
    SPLIT_PART(TRIM(full_name), ' ', 1)      AS first_name,
    SPLIT_PART(TRIM(full_name), ' ', 2)      AS last_name
FROM customers
ORDER BY customer_id;
```

### Problem 3 (Medium) — Find dirty phones and show cleaned version
```sql
SELECT
    customer_id,
    full_name,
    phone                                             AS phone_raw,
    REGEXP_REPLACE(TRIM(phone), '[^0-9]', '', 'g')   AS phone_clean
FROM customers
WHERE REGEXP_REPLACE(TRIM(phone), '[^0-9]', '', 'g')
      !~ '^[0-9]{10}$'          -- non-digit chars exist or length != 10
ORDER BY customer_id;
```

---

## 11. Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| `WHERE email = 'alice@gmail.com'` | Fails if email has spaces or mixed case | `WHERE TRIM(LOWER(email)) = 'alice@gmail.com'` |
| `TRIM` removes specific substring | `TRIM` removes characters, not substrings | Use `REPLACE` or `REGEXP_REPLACE` |
| `SUBSTRING` index is 0-based | SQL `SUBSTRING` is **1-based** | `SUBSTRING(s FROM 1 FOR 4)` for first 4 chars |
| `||` with NULL | `NULL || 'x'` → `NULL` | Use `CONCAT()` or `COALESCE(col, '')` |
| `SPLIT_PART` on name with middle name | Returns empty for missing part | Handle with `CASE WHEN` or check part count |

---

## 12. Quick Reference

```sql
-- Case
UPPER(s)  LOWER(s)  INITCAP(s)

-- Trim
TRIM(s)  LTRIM(s)  RTRIM(s)
TRIM(BOTH 'x' FROM s)

-- Length
LENGTH(s)  CHAR_LENGTH(s)

-- Find position
POSITION('x' IN s)    -- 1-based, 0 if not found
STRPOS(s, 'x')        -- same

-- Substring
SUBSTRING(s FROM start FOR len)
SPLIT_PART(s, ',', 1) -- 1-indexed field

-- Replace
REPLACE(s, 'old', 'new')
REGEXP_REPLACE(s, '[^0-9]', '', 'g')

-- Concat
CONCAT(a, b, c)        -- null-safe
a || b                 -- null propagates
CONCAT_WS(',', a, b)   -- with separator, skips nulls

-- Useful combos
TRIM(LOWER(email))
INITCAP(TRIM(full_name))
SPLIT_PART(TRIM(full_name), ' ', 1)   -- first name
REGEXP_REPLACE(phone, '[^0-9]', '', 'g')  -- digits only
```
