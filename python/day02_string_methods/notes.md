# Day 2 — Python: String Methods & Manipulation

> **Roadmap Day:** 2 · **Date:** Tuesday, June 16, 2026  
> **Study Window:** 9 PM – 11 PM  
> **Interview Level:** Easy → Medium

---

## 1. Strings Are Immutable Sequences

A Python string is an **immutable** sequence of Unicode characters. Every string method returns a **new** string — the original is never modified.

```python
s = "  Hello, World!  "
result = s.strip()
print(s)       # "  Hello, World!  "  ← unchanged
print(result)  # "Hello, World!"      ← new string
```

**Key mental model:** Strings in Python are values, not mutable containers. Chain methods to build transformations step by step.

---

## 2. Case Conversion

| Method | What it does |
|--------|-------------|
| `s.upper()` | All characters → uppercase |
| `s.lower()` | All characters → lowercase |
| `s.title()` | First letter of each word → uppercase |
| `s.capitalize()` | First letter → uppercase, rest → lowercase |
| `s.swapcase()` | Uppercase ↔ lowercase |

```python
name = "alice johnson"

print(name.upper())       # ALICE JOHNSON
print(name.title())       # Alice Johnson
print(name.capitalize())  # Alice johnson
```

**DE context:** Standardise column values before comparison — `"Engineering"` vs `"engineering"` vs `"ENGINEERING"` are all equal after `.lower()`.

---

## 3. Whitespace & Strip

| Method | What it does |
|--------|-------------|
| `s.strip()` | Remove leading + trailing whitespace |
| `s.lstrip()` | Remove leading (left) whitespace only |
| `s.rstrip()` | Remove trailing (right) whitespace only |
| `s.strip(chars)` | Remove specific characters from both ends |

```python
raw = "   data engineer   "

print(repr(raw.strip()))   # 'data engineer'
print(repr(raw.lstrip()))  # 'data engineer   '
print(repr(raw.rstrip()))  # '   data engineer'

# Strip specific characters (not just spaces)
tag = "###IMPORTANT###"
print(tag.strip("#"))   # IMPORTANT
```

**DE context:** Raw CSV/API data almost always has stray whitespace. Always `.strip()` before inserting into a database or comparing values.

---

## 4. Split & Join

```python
# split(sep, maxsplit) — splits into a list
line = "2024-01-15,ERROR,user=john,status=failed"

parts = line.split(",")
# ['2024-01-15', 'ERROR', 'user=john', 'status=failed']

# Limit splits with maxsplit
date, rest = line.split(",", maxsplit=1)
# date = '2024-01-15'
# rest = 'ERROR,user=john,status=failed'

# split without argument — splits on any whitespace, strips leading/trailing
words = "  hello   world  ".split()
# ['hello', 'world']
```

```python
# join(iterable) — inverse of split
parts = ["2024-01-15", "ERROR", "user=john"]
line  = ",".join(parts)
# '2024-01-15,ERROR,user=john'

# Build pipe-delimited row
cols = ["Alice", "Engineering", "95000"]
print("|".join(cols))   # Alice|Engineering|95000
```

**Key distinction:** `split()` is called on the **separator**, `join()` is called on the **separator** too — `sep.join(list)`.

---

## 5. Find, Replace, Count

```python
text = "user=john action=login status=failed action=retry"

# find(sub) — returns first index, or -1 if not found
print(text.find("action"))   # 11
print(text.find("xyz"))      # -1

# index(sub) — same but raises ValueError if not found
# print(text.index("xyz"))  # ValueError — don't use unless you know it exists

# count(sub) — count non-overlapping occurrences
print(text.count("action"))  # 2

# replace(old, new, count=None)
cleaned = text.replace("action=", "event=")
# 'user=john event=login status=failed event=retry'

# Replace only first occurrence
first_only = text.replace("action=", "event=", 1)
# 'user=john event=login status=failed action=retry'
```

---

## 6. startswith, endswith, in

```python
filename = "orders_2024_01.csv"

# startswith / endswith — exact prefix/suffix check
print(filename.startswith("orders"))  # True
print(filename.endswith(".csv"))       # True
print(filename.endswith((".csv", ".tsv")))  # True — tuple of suffixes

# in operator — substring membership
print(".csv" in filename)  # True
print(".parquet" in filename)  # False
```

**DE context:** Filter files by extension, check if a log line is an ERROR, validate field names — all use these.

---

## 7. String Formatting

### f-strings (preferred)
```python
name   = "Alice"
salary = 95000

print(f"{name} earns ${salary:,}")          # Alice earns $95,000
print(f"{salary:.2f}")                      # 95000.00
print(f"{name:<10} | {salary:>8,}")         # Alice      |   95,000
print(f"{'HEADER':^20}")                    # centered in 20 chars
```

### format() — older but still common in templates
```python
template = "User: {name} | Dept: {dept} | Salary: {salary:,}"
print(template.format(name="Bob", dept="Finance", salary=72000))
```

---

## 8. Substring Extraction (Slicing)

```python
s = "2024-01-15 ERROR user=john"

# s[start:stop:step]
print(s[0:4])    # '2024'   — year
print(s[5:7])    # '01'     — month
print(s[8:10])   # '15'     — day
print(s[:10])    # '2024-01-15'  — date portion
print(s[11:])    # 'ERROR user=john'
print(s[-4:])    # 'john'   — last 4 chars
print(s[::-1])   # reversed string
```

---

## 9. Parsing Patterns — Real DE Usage

### Parse key=value log lines
```python
log = "2024-01-15 ERROR user=john action=login status=failed"

# Approach 1: split on spaces, then split each token on '='
parts  = log.split()
date   = parts[0]   # '2024-01-15'
level  = parts[1]   # 'ERROR'
fields = {}

for part in parts[2:]:
    if "=" in part:
        key, value = part.split("=", 1)   # maxsplit=1 handles value with '='
        fields[key] = value

result = {"date": date, "level": level, **fields}
# {'date': '2024-01-15', 'level': 'ERROR', 'user': 'john',
#  'action': 'login', 'status': 'failed'}
```

### Parse CSV row into dict
```python
def parse_csv_row(header_line, data_line):
    headers = [h.strip() for h in header_line.split(",")]
    values  = [v.strip() for v in data_line.split(",")]
    return dict(zip(headers, values))

header = "customer_id, full_name, email, city"
data   = "101, Alice Johnson , alice@gmail.com , Mumbai"

record = parse_csv_row(header, data)
# {'customer_id': '101', 'full_name': 'Alice Johnson', 'email': 'alice@gmail.com', 'city': 'Mumbai'}
```

### Domain extraction from emails
```python
emails = ["alice@gmail.com", "bob@yahoo.com", "carol@gmail.com", "dave@hotmail.com"]

domain_counts = {}
for email in emails:
    domain = email.split("@")[1]           # 'gmail.com'
    domain_counts[domain] = domain_counts.get(domain, 0) + 1

# {'gmail.com': 2, 'yahoo.com': 1, 'hotmail.com': 1}
```

---

## 10. Day 2 Problems — Solutions

### Problem 1 (Easy) — Parse CSV row into dict
```python
def parse_csv_row(row: str) -> dict:
    fields = ["date", "level", "user", "action", "status"]
    # This problem is actually about a log row, not CSV
    # Using split + dict(zip(...))
    parts   = row.split(",")
    headers = ["customer_id", "name", "email", "city"]
    return dict(zip(headers, [p.strip() for p in parts]))

row = "101, Alice Johnson, alice@gmail.com, Mumbai"
print(parse_csv_row(row))
# {'customer_id': '101', 'name': 'Alice Johnson', 'email': 'alice@gmail.com', 'city': 'Mumbai'}
```

### Problem 2 (Easy) — Email domain counter
```python
emails = [
    "alice@gmail.com", "bob@yahoo.com", "carol@gmail.com",
    "dave@hotmail.com", "eve@gmail.com", "frank@yahoo.com"
]

domain_counts = {}
for email in emails:
    domain = email.split("@")[1].lower().strip()
    domain_counts[domain] = domain_counts.get(domain, 0) + 1

print(sorted(domain_counts.items(), key=lambda x: -x[1]))
# [('gmail.com', 3), ('yahoo.com', 2), ('hotmail.com', 1)]
```

### Problem 3 (Medium) — Parse structured log line
```python
log = "2024-01-15 ERROR user=john action=login status=failed"

parts  = log.split()
result = {"date": parts[0], "level": parts[1]}

for token in parts[2:]:
    if "=" in token:
        k, v = token.split("=", 1)
        result[k] = v

print(result)
# {'date': '2024-01-15', 'level': 'ERROR', 'user': 'john', 'action': 'login', 'status': 'failed'}
```

---

## 11. Interview Checklist

| Question | Answer |
|----------|--------|
| Are strings mutable in Python? | No — every method returns a new string |
| `split()` vs `split(" ")`? | `split()` handles multiple spaces + strips; `split(" ")` gives empty strings for consecutive spaces |
| `find()` vs `index()`? | `find()` returns -1 on miss; `index()` raises `ValueError` |
| `strip()` vs `replace(" ", "")`? | `strip()` only removes leading/trailing; `replace` removes ALL spaces |
| How to check if string is numeric? | `s.isdigit()`, `s.isnumeric()`, or `try: float(s)` |
| How to remove non-digit chars from phone? | `"".join(c for c in phone if c.isdigit())` |
| How to split "Alice Johnson" into first/last? | `first, last = "Alice Johnson".split(maxsplit=1)` |

---

## 12. Quick Reference

```python
# Case
s.upper()  s.lower()  s.title()  s.capitalize()

# Strip
s.strip()  s.lstrip()  s.rstrip()  s.strip("#")

# Split / Join
s.split(",")          # split on comma
s.split(maxsplit=2)   # max 2 splits
s.split()             # split on whitespace, strips
",".join(list)        # join list into string

# Find / Replace / Count
s.find("x")           # index or -1
s.count("x")          # occurrences
s.replace("old","new") # all replacements
s.replace("o","n",1)  # first replacement only

# Check
s.startswith("pre")   s.endswith(".csv")
"sub" in s            s.isdigit()  s.isalpha()

# Slice
s[0:4]   s[-1]   s[::-1]

# Format
f"{val:,}"   f"{val:.2f}"   f"{val:<10}"

# Useful one-liners
"".join(c for c in s if c.isdigit())  # digits only
[p.strip() for p in s.split(",")]     # split + strip each part
email.split("@")[1]                   # domain from email
```
