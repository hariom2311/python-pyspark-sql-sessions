# Day 2 — PySpark: String Column Functions

> **Roadmap Day:** 2 · **Date:** Tuesday, June 16, 2026  
> **Study Window:** 9 PM – 11 PM  
> **Note:** Same problems as SQL Day 2 — same data, same logic, different syntax

---

## 1. PySpark vs SQL Mental Model

| SQL Function | PySpark Equivalent | Notes |
|-------------|-------------------|-------|
| `UPPER(col)` | `upper(col("x"))` | Import from `pyspark.sql.functions` |
| `LOWER(col)` | `lower(col("x"))` | |
| `INITCAP(col)` | `initcap(col("x"))` | Title case |
| `TRIM(col)` | `trim(col("x"))` | Both sides |
| `LTRIM(col)` | `ltrim(col("x"))` | Left only |
| `RTRIM(col)` | `rtrim(col("x"))` | Right only |
| `REPLACE(col,'a','b')` | `regexp_replace(col("x"), "a", "b")` | Or `translate()` |
| `REGEXP_REPLACE(col, pat, '', 'g')` | `regexp_replace(col("x"), pat, "")` | Global by default in Spark |
| `SUBSTRING(col FROM 1 FOR 4)` | `substring(col("x"), 1, 4)` | 1-based index |
| `CONCAT(a, b)` | `concat(col("a"), col("b"))` | |
| `CONCAT_WS(',', a, b)` | `concat_ws(",", col("a"), col("b"))` | Skips nulls |
| `SPLIT_PART(col, ' ', 1)` | `split(col("x"), " ")[0]` | 0-indexed in Spark |
| `LENGTH(col)` | `length(col("x"))` | |
| `POSITION('@' IN col)` | `instr(col("x"), "@")` | 1-based, 0 if not found |

---

## 2. Setup

```python
import os

os.environ['JAVA_HOME']             = 'C:/Program Files/DBeaver/jre'
os.environ['PYSPARK_PYTHON']        = r'C:\Users\hariom\AppData\Local\Programs\Python\Python311\python.exe'
os.environ['PYSPARK_DRIVER_PYTHON'] = r'C:\Users\hariom\AppData\Local\Programs\Python\Python311\python.exe'

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, upper, lower, initcap, trim, ltrim, rtrim,
    regexp_replace, substring, length, instr,
    concat, concat_ws, split, when, lit
)

spark = SparkSession.builder \
    .appName("Day02_StringFunctions") \
    .master("local[*]") \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")
```

---

## 3. upper() / lower() / initcap()

```python
from pyspark.sql.functions import upper, lower, initcap

df.select(
    col("email"),
    lower(trim(col("email"))).alias("email_clean"),
    initcap(trim(col("full_name"))).alias("name_clean")
).show(truncate=False)

# DE pattern: standardise before comparison
df.filter(lower(trim(col("email"))) == "alice@gmail.com")
```

---

## 4. trim() / ltrim() / rtrim()

```python
from pyspark.sql.functions import trim, ltrim, rtrim

df.withColumn("name_clean",  trim(col("full_name"))) \
  .withColumn("email_clean", trim(col("email"))) \
  .withColumn("phone_clean", trim(col("phone"))) \
  .show(truncate=False)

# trim a specific character — use regexp_replace instead
df.withColumn("phone_no_plus", regexp_replace(col("phone"), r"^\+", ""))
```

---

## 5. regexp_replace() — Pattern-Based Replacement

```python
from pyspark.sql.functions import regexp_replace

# Remove all non-digit characters from phone
df.withColumn(
    "phone_clean",
    regexp_replace(trim(col("phone")), r"[^0-9]", "")
).select("customer_id", "phone", "phone_clean").show(truncate=False)

# Normalise multiple whitespace to single space
from pyspark.sql.functions import regexp_replace
df.withColumn("name_norm", trim(regexp_replace(col("full_name"), r"\s+", " ")))
```

**Key difference from SQL:** Spark's `regexp_replace` replaces ALL matches by default — no 'g' flag needed.

---

## 6. split() — Split String into Array

```python
from pyspark.sql.functions import split

# Split full_name into first and last name
df.withColumn("name_parts", split(trim(col("full_name")), " ")) \
  .withColumn("first_name", split(trim(col("full_name")), " ")[0]) \
  .withColumn("last_name",  split(trim(col("full_name")), " ")[1]) \
  .select("full_name", "first_name", "last_name") \
  .show(truncate=False)
```

**IMPORTANT:** `split()` returns an **ArrayType** column. Access elements with `[0]`, `[1]` — **0-indexed** (unlike SQL's `SPLIT_PART` which is 1-indexed).

---

## 7. substring() — Extract Part of String

```python
from pyspark.sql.functions import substring

# Extract year / month / day from date string "2024-01-15"
df.withColumn("year",  substring(col("order_date"), 1, 4)) \
  .withColumn("month", substring(col("order_date"), 6, 2)) \
  .withColumn("day",   substring(col("order_date"), 9, 2))

# Extract domain from email
from pyspark.sql.functions import instr
df.withColumn(
    "domain",
    substring(col("email"), instr(col("email"), "@") + 1, 100)
).show()
```

`substring(col, pos, len)` — **1-based** position, same as SQL.

---

## 8. concat() / concat_ws()

```python
from pyspark.sql.functions import concat, concat_ws, lit

# concat — null propagates if any argument is null
df.withColumn(
    "display_label",
    concat(initcap(trim(col("full_name"))), lit(" <"), lower(trim(col("email"))), lit(">"))
)

# concat_ws — separator + null-safe (skips null values)
df.withColumn(
    "address_full",
    concat_ws(", ", col("city"), col("state"), col("country"))
)

# Build a pipe-delimited string
df.withColumn("row_key", concat_ws("|", col("customer_id"), col("email")))
```

---

## 9. length() / instr()

```python
from pyspark.sql.functions import length, instr

# Length of cleaned phone — should be 10 digits
df.withColumn("phone_clean", regexp_replace(trim(col("phone")), r"[^0-9]", "")) \
  .withColumn("phone_len", length(col("phone_clean"))) \
  .filter(col("phone_len") != 10) \
  .select("customer_id", "full_name", "phone", "phone_clean", "phone_len") \
  .show(truncate=False)

# instr — find position of substring (1-based, 0 if not found)
df.withColumn("at_pos", instr(col("email"), "@")) \
  .withColumn("has_at", instr(col("email"), "@") > 0) \
  .show()
```

---

## 10. Day 2 Problems — PySpark Solutions

### Problem 1 (Easy) — Standardise emails
```python
df.withColumn("email_clean", lower(trim(col("email")))) \
  .select("customer_id", "email", "email_clean") \
  .orderBy("customer_id") \
  .show(truncate=False)
```

### Problem 2 (Easy) — Split full_name into first and last
```python
df.withColumn("first_name", split(trim(col("full_name")), r"\s+")[0]) \
  .withColumn("last_name",  split(trim(col("full_name")), r"\s+")[1]) \
  .select("customer_id", trim(col("full_name")).alias("full_name"), "first_name", "last_name") \
  .orderBy("customer_id") \
  .show(truncate=False)
```

### Problem 3 (Medium) — Find dirty phones and show cleaned version
```python
df.withColumn("phone_clean", regexp_replace(trim(col("phone")), r"[^0-9]", "")) \
  .filter(length(col("phone_clean")) != 10) \
  .select("customer_id", "full_name", "phone", "phone_clean") \
  .orderBy("customer_id") \
  .show(truncate=False)
```

---

## 11. filter() vs SQL String comparison

| Task | SQL | PySpark |
|------|-----|---------|
| Case-insensitive equals | `LOWER(email) = 'x'` | `lower(col("email")) == "x"` |
| Contains substring | `email LIKE '%@%'` | `col("email").contains("@")` |
| Starts with | `name LIKE 'A%'` | `col("name").startswith("A")` |
| Ends with | `file LIKE '%.csv'` | `col("file").endswith(".csv")` |
| Regex match | `email ~ '^[a-z]+'` | `col("email").rlike("^[a-z]+")` |
| Not contains | `email NOT LIKE '%@%'` | `~col("email").contains("@")` |

---

## 12. Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| `split(...)[0]` is 0-indexed | SQL `SPLIT_PART` is 1-indexed | In PySpark use `[0]` for first element |
| `regexp_replace` has no 'g' flag | Already global by default | Just omit the flag — all matches replaced |
| Comparing with `==` on Column | `col("x") == col("y")` works; `col("x") == None` doesn't | Use `.isNull()` for null checks |
| `trim()` only trims spaces | Can't trim arbitrary chars with `trim()` | Use `regexp_replace(col, r"^x+|x+$", "")` |
| `substring(col, 0, 4)` | PySpark `substring` is 1-based | Use `substring(col, 1, 4)` for first 4 chars |

---

## 13. Quick Reference

```python
from pyspark.sql.functions import (
    upper, lower, initcap,          # case
    trim, ltrim, rtrim,             # whitespace
    regexp_replace,                 # pattern replace
    split, substring,               # split / slice
    concat, concat_ws, lit,         # concat
    length, instr,                  # length / find
    when, col                       # control flow / column ref
)

# Case
upper(col("x"))   lower(col("x"))   initcap(col("x"))

# Trim
trim(col("x"))    ltrim(col("x"))   rtrim(col("x"))

# Replace
regexp_replace(col("x"), r"[^0-9]", "")   # digits only
regexp_replace(col("x"), r"\s+", " ")     # collapse spaces

# Split (returns Array — 0-indexed)
split(col("x"), " ")[0]   # first word
split(col("x"), ",")[1]   # second element

# Substring (1-based)
substring(col("x"), 1, 4)   # first 4 chars
substring(col("x"), 6, 2)   # 2 chars starting at pos 6

# Concat
concat(col("a"), lit("-"), col("b"))
concat_ws(",", col("a"), col("b"), col("c"))

# Length / Find
length(col("x"))            # string length
instr(col("x"), "@")        # position, 0 if not found

# String predicates
col("x").contains("@")
col("x").startswith("A")
col("x").endswith(".csv")
col("x").rlike(r"^[0-9]+$")
~col("x").contains("@")     # NOT contains
```
