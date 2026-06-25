# Day 5 — Python: File Handling (CSV, JSON, TXT)

> **Roadmap Day:** 5 · **Date:** Friday, June 19, 2026  
> **Study Window:** 9 PM – 11 PM  
> **Interview Level:** Easy → Medium

---

## 1. Why File Handling Matters for Data Engineers

Every pipeline touches files: raw CSVs from vendors, JSON from APIs, log files from systems. Reading them correctly — without pandas, with generators, with proper error handling — is a basic DE competency.

---

## 2. Reading CSV — `csv` Module

```python
import csv

# csv.reader — rows as lists
with open('employees.csv', newline='') as f:
    reader = csv.reader(f)
    header = next(reader)          # skip header row
    for row in reader:
        print(row)                 # ['Alice', 'Engineering', '95000']

# csv.DictReader — rows as dicts (column name → value)
with open('employees.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row['name'], row['salary'])

# csv.writer — write rows
with open('out.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['name', 'dept', 'salary'])   # header
    writer.writerows([['Alice', 'Eng', 95000]])    # data
```

**Key parameter:** `newline=''` on open — prevents double newlines on Windows.

---

## 3. Reading JSON — `json` Module

```python
import json

# Read entire file
with open('orders.json') as f:
    data = json.load(f)            # returns dict or list

# Read JSON lines (one JSON object per line — common in DE)
with open('events.jsonl') as f:
    records = [json.loads(line) for line in f]

# Write JSON
with open('out.json', 'w') as f:
    json.dump(data, f, indent=2)

# Write JSON lines
with open('out.jsonl', 'w') as f:
    for record in records:
        f.write(json.dumps(record) + '\n')

# Parse JSON string (API response)
raw = '{"order_id": 1, "status": "completed"}'
obj = json.loads(raw)              # string → dict
```

---

## 4. Reading TXT / Log Files

```python
# Read all lines at once (small files only)
with open('app.log') as f:
    lines = f.readlines()          # list of strings, '\n' included

# Read line by line — O(1) memory regardless of file size
with open('app.log') as f:
    for line in f:
        line = line.strip()        # remove trailing '\n'
        if 'ERROR' in line:
            print(line)

# Write text
with open('errors.log', 'w') as f:
    f.write('ERROR 2024-01-15 login failed\n')
```

---

## 5. Generator Pattern for Large Files

A **generator** yields one item at a time — never loads the full file into memory.

```python
def read_csv_chunks(path, chunk_size=1000):
    """Yield rows in chunks — safe for 10M-row files."""
    import csv
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        chunk = []
        for row in reader:
            chunk.append(row)
            if len(chunk) == chunk_size:
                yield chunk
                chunk = []
        if chunk:                  # yield last partial chunk
            yield chunk

# Usage
for chunk in read_csv_chunks('big.csv'):
    process(chunk)                 # process 1000 rows at a time
```

```python
def error_lines(path):
    """Generator — yields only ERROR lines from log file."""
    with open(path) as f:
        for line in f:
            if 'ERROR' in line:
                yield line.strip()

# Usage
for err in error_lines('app.log'):
    print(err)
```

---

## 6. Aggregation from CSV (without pandas)

```python
import csv
from collections import defaultdict

def avg_salary_by_dept(path):
    totals = defaultdict(lambda: {'total': 0, 'count': 0})
    with open(path, newline='') as f:
        for row in csv.DictReader(f):
            dept = row['dept']
            totals[dept]['total'] += float(row['salary'])
            totals[dept]['count'] += 1
    return {
        dept: round(v['total'] / v['count'], 2)
        for dept, v in totals.items()
    }
```

---

## 7. Day 5 Problem Solutions

### Q1 — Average salary per department from CSV

```python
import csv
from collections import defaultdict

def avg_salary_by_dept(path):
    acc = defaultdict(lambda: {'total': 0.0, 'count': 0})
    with open(path, newline='') as f:
        for row in csv.DictReader(f):
            dept = row['dept'].strip()
            acc[dept]['total'] += float(row['salary'])
            acc[dept]['count'] += 1
    return {d: round(v['total'] / v['count'], 2) for d, v in acc.items()}
```

### Q2 — Filter JSON orders, write completed ones

```python
import json

def filter_completed_orders(in_path, out_path):
    with open(in_path) as f:
        orders = json.load(f)
    completed = [o for o in orders if o.get('status') == 'completed']
    with open(out_path, 'w') as f:
        json.dump(completed, f, indent=2)
    return len(completed)
```

### Q3 — Extract ERROR lines via generator

```python
def extract_errors(log_path, out_path):
    def error_lines(path):
        with open(path) as f:
            for line in f:
                if 'ERROR' in line:
                    yield line.strip()

    with open(out_path, 'w') as out:
        count = 0
        for err in error_lines(log_path):
            out.write(err + '\n')
            count += 1
    return count
```

---

## 8. Interview Checklist

- [ ] Read CSV with `csv.DictReader` — rows as dicts
- [ ] Write CSV with `csv.writer` — remember `newline=''`
- [ ] Parse JSON file: `json.load(f)` vs string: `json.loads(s)`
- [ ] Read file line-by-line in a loop — O(1) memory
- [ ] Write a generator that reads a large file in chunks
- [ ] Compute grouped aggregation from CSV without pandas

---

## 9. Quick Reference

| Task | Code |
|------|------|
| Read CSV as dicts | `csv.DictReader(f)` |
| Write CSV rows | `csv.writer(f).writerows(rows)` |
| Parse JSON file | `json.load(f)` |
| Parse JSON string | `json.loads(s)` |
| Write JSON | `json.dump(obj, f, indent=2)` |
| Read file line by line | `for line in f: line.strip()` |
| Generator for large file | `yield row` inside `with open(...)` |
| Group + aggregate from CSV | `defaultdict` + `csv.DictReader` |
