# Tricky Questions — Day 1 to Day 4
## Python · SQL · PySpark | Quick-fire gotchas

> These are **not hard problems** — they are tricky because the answer looks obvious but isn't.  
> Each question fits in < 5 lines. Predict the output, then verify in Python.  
> No IDE hints — think it through first.

---

## PYTHON TRICKY QUESTIONS

---

### Day 1 — Loops, Enumerate, Zip

---

**P1.1 — What does `enumerate` start from?**

```python
items = ['a', 'b', 'c']
for i, v in enumerate(items, start=1):
    print(i, v)
```
What is the first line printed?

<details><summary>Answer</summary>

`1 a`  
`enumerate(items, start=1)` starts the counter at 1, not 0.  
Default is `start=0` — always check which you need.

</details>

---

**P1.2 — zip stops at the shortest**

```python
names   = ['Alice', 'Bob', 'Carol']
scores  = [90, 85]

result = list(zip(names, scores))
print(result)
```
What is `result`?

<details><summary>Answer</summary>

`[('Alice', 90), ('Bob', 85)]`  
`zip` stops at the **shorter** iterable. `'Carol'` is silently dropped.  
Use `itertools.zip_longest` if you need all elements.

</details>

---

**P1.3 — for-else: when does `else` run?**

```python
nums = [1, 3, 5, 7]
for n in nums:
    if n % 2 == 0:
        print('found even')
        break
else:
    print('no even found')
```
What is printed?

<details><summary>Answer</summary>

`no even found`  
The `else` block of a for loop runs when the loop **completes without hitting `break`**.  
Classic interview gotcha — most people forget `for-else` exists.

</details>

---

**P1.4 — continue vs break**

```python
total = 0
for i in range(1, 6):
    if i == 3:
        continue
    total += i
print(total)
```
What is `total`?

<details><summary>Answer</summary>

`12`  
`continue` skips iteration 3, so: 1 + 2 + 4 + 5 = 12.  
`break` would have given 1 + 2 = 3.

</details>

---

**P1.5 — zip with unzip**

```python
pairs = [(1, 'a'), (2, 'b'), (3, 'c')]
nums, letters = zip(*pairs)
print(nums)
print(letters)
```
What are `nums` and `letters`?

<details><summary>Answer</summary>

```
(1, 2, 3)
('a', 'b', 'c')
```
`zip(*pairs)` is the classic **unzip** trick — `*` unpacks the list, `zip` transposes it.  
Both results are **tuples**, not lists.

</details>

---

**P1.6 — enumerate does not give you a list**

```python
items = ['x', 'y', 'z']
e = enumerate(items)
print(type(e))
print(list(e))
print(list(e))   # second time
```
What does the second `list(e)` print?

<details><summary>Answer</summary>

```
<class 'enumerate'>
[(0, 'x'), (1, 'y'), (2, 'z')]
[]
```
`enumerate` returns a **lazy iterator**. Once exhausted, it gives nothing.  
Same gotcha applies to `zip`, `map`, `filter`.

</details>

---

### Day 2 — Strings

---

**P2.1 — split() with no argument vs split(' ')**

```python
s = '  hello   world  '
print(s.split())       # no argument
print(s.split(' '))    # explicit space
```
What is the difference?

<details><summary>Answer</summary>

```python
['hello', 'world']                           # split() — strips and splits on any whitespace
['', '', 'hello', '', '', 'world', '', '']   # split(' ') — splits on exactly one space
```
`split()` with no args collapses all whitespace and strips edges.  
`split(' ')` is literal — every space is a delimiter, giving empty strings.

</details>

---

**P2.2 — String immutability: what happens here?**

```python
s = 'hello'
s[0] = 'H'
```
What is the result?

<details><summary>Answer</summary>

`TypeError: 'str' object does not support item assignment`  
Strings are **immutable** in Python. To change a character: `s = 'H' + s[1:]`

</details>

---

**P2.3 — Slicing a string**

```python
s = 'abcdefgh'
print(s[2:6])
print(s[-3:])
print(s[::2])
print(s[::-1])
```
Predict all four outputs.

<details><summary>Answer</summary>

```
cdef        # index 2 up to (not including) 6
fgh         # last 3 characters
aceg        # every second character
hgfedcba   # reversed
```
Step syntax: `s[start:stop:step]`. `step=-1` reverses.

</details>

---

**P2.4 — `in` on strings is substring, not character-only**

```python
print('cat' in 'concatenate')
print('cat' in ['dog', 'cat', 'bird'])
```
What do both lines print?

<details><summary>Answer</summary>

```
True
True
```
For strings, `in` checks **substring**. `'cat'` is inside `'concatenate'`.  
For lists, `in` checks **element equality**.  
Both are `True` but for different reasons.

</details>

---

**P2.5 — strip vs lstrip vs rstrip**

```python
s = '  hello  '
print(repr(s.strip()))
print(repr(s.lstrip()))
print(repr(s.rstrip()))
```
What does each print?

<details><summary>Answer</summary>

```
'hello'
'hello  '
'  hello'
```
`strip()` both sides. `lstrip()` left only. `rstrip()` right only.  
Always use `repr()` when checking whitespace — it shows the spaces explicitly.

</details>

---

**P2.6 — String multiplication and join**

```python
print('-' * 5)
print(''.join(['a', 'b', 'c']))
print(','.join(['a', 'b', 'c']))
```

<details><summary>Answer</summary>

```
-----
abc
a,b,c
```
`join` takes an **iterable of strings**. The string before `.join()` is the separator — empty string means no separator.

</details>

---

**P2.7 — `replace` is not in-place**

```python
s = 'hello world'
s.replace('world', 'python')
print(s)
```
What is printed?

<details><summary>Answer</summary>

`hello world`  
Strings are immutable — `replace` returns a **new string**, it doesn't modify `s`.  
Fix: `s = s.replace('world', 'python')`

</details>

---

**P2.8 — map returns an iterator, not a list**

```python
nums = ['1', '2', '3']
result = map(int, nums)
print(result)
print(list(result))
print(list(result))   # second time
```

<details><summary>Answer</summary>

```
<map object at 0x...>
[1, 2, 3]
[]
```
`map()` is a **lazy iterator**. Like `enumerate` and `zip`, it exhausts after one pass.  
Always wrap in `list()` or iterate once if you need to reuse.

</details>

---

**P2.9 — filter keeps Truthy values**

```python
data = [0, 1, '', 'hello', None, 42, False, True]
result = list(filter(None, data))
print(result)
```
What is `result`?

<details><summary>Answer</summary>

`[1, 'hello', 42, True]`  
`filter(None, iterable)` keeps items that are **truthy**.  
Falsy values: `0`, `''`, `None`, `False`, `[]`, `{}`.

</details>

---

**P2.10 — reduce to multiply all elements**

```python
from functools import reduce
nums = [1, 2, 3, 4, 5]
result = reduce(lambda acc, x: acc * x, nums)
print(result)
```

<details><summary>Answer</summary>

`120`  
`reduce` applies the function cumulatively: `((((1×2)×3)×4)×5) = 120`.  
This is the **factorial** of 5. `reduce` with `+` gives sum; with `*` gives product.

</details>

---

### Day 3 — Lists & Arrays

---

**P3.1 — List assignment is not a copy**

```python
a = [1, 2, 3]
b = a
b.append(4)
print(a)
```
What is `a`?

<details><summary>Answer</summary>

`[1, 2, 3, 4]`  
`b = a` makes `b` point to the **same list object**.  
Fix: `b = a.copy()` or `b = a[:]` for a shallow copy.

</details>

---

**P3.2 — List slicing IS a copy**

```python
a = [1, 2, 3]
b = a[:]
b.append(4)
print(a)
print(b)
```

<details><summary>Answer</summary>

```
[1, 2, 3]
[1, 2, 3, 4]
```
Slicing `a[:]` creates a **new list** (shallow copy). `a` is unaffected.  
Contrast with `b = a` which shares the same object.

</details>

---

**P3.3 — Shallow copy and nested lists**

```python
import copy
a = [[1, 2], [3, 4]]
b = a.copy()
b[0].append(99)
print(a)
```
What is `a`?

<details><summary>Answer</summary>

`[[1, 2, 99], [3, 4]]`  
`a.copy()` is **shallow** — the outer list is new, but inner lists are still shared references.  
Fix: `b = copy.deepcopy(a)` to get fully independent nested structures.

</details>

---

**P3.4 — list.sort() vs sorted()**

```python
a = [3, 1, 2]
b = a.sort()
print(a)
print(b)
```

<details><summary>Answer</summary>

```
[1, 2, 3]
None
```
`a.sort()` sorts **in-place** and returns `None`.  
`sorted(a)` returns a **new sorted list** and leaves `a` unchanged.  
Classic mistake: `b = a.sort()` then using `b`.

</details>

---

**P3.5 — Mutable default argument**

```python
def add_item(item, lst=[]):
    lst.append(item)
    return lst

print(add_item('a'))
print(add_item('b'))
print(add_item('c'))
```

<details><summary>Answer</summary>

```
['a']
['a', 'b']
['a', 'b', 'c']
```
The default list `[]` is created **once** and reused across calls.  
Fix: `def add_item(item, lst=None): if lst is None: lst = []`

</details>

---

**P3.6 — List multiplication shares references**

```python
matrix = [[0] * 3] * 3
matrix[0][0] = 9
print(matrix)
```
What is `matrix`?

<details><summary>Answer</summary>

```
[[9, 0, 0], [9, 0, 0], [9, 0, 0]]
```
`[[0]*3] * 3` creates 3 references to the **same inner list**.  
Fix: `matrix = [[0]*3 for _ in range(3)]` — each row is a new list.

</details>

---

**P3.7 — Negative index**

```python
lst = [10, 20, 30, 40, 50]
print(lst[-1])
print(lst[-2])
print(lst[-5])
```

<details><summary>Answer</summary>

```
50
40
10
```
`lst[-1]` is the last element, `lst[-n]` is the nth from the end.  
`lst[-5]` equals `lst[0]` for a 5-element list.

</details>

---

**P3.8 — del vs remove vs pop**

```python
lst = [10, 20, 30, 20, 40]
lst.remove(20)
print(lst)
```

<details><summary>Answer</summary>

`[10, 30, 20, 40]`  
`remove(x)` deletes the **first occurrence** of `x`.  
`del lst[i]` removes by index. `pop(i)` removes by index and **returns** the value.

</details>

---

### Day 4 — Dictionary & HashMap

---

**P4.1 — Dictionary key lookup: missing key**

```python
d = {'a': 1, 'b': 2}
print(d['c'])
```

<details><summary>Answer</summary>

`KeyError: 'c'`  
Use `d.get('c')` → returns `None`.  
Use `d.get('c', 0)` → returns default `0`.

</details>

---

**P4.2 — dict.get vs dict[]**

```python
d = {'x': 0, 'y': None}
print(d.get('x', 'missing'))
print(d.get('y', 'missing'))
print(d.get('z', 'missing'))
```

<details><summary>Answer</summary>

```
0
None
missing
```
`get(key, default)` returns `default` only when the **key is absent** — NOT when the value is falsy.  
`d['y']` is `None` (key exists), so `get` returns `None`, not `'missing'`.

</details>

---

**P4.3 — Dict update merges, not replaces**

```python
a = {'x': 1, 'y': 2}
b = {'y': 99, 'z': 3}
a.update(b)
print(a)
```

<details><summary>Answer</summary>

`{'x': 1, 'y': 99, 'z': 3}`  
`update` overwrites existing keys and adds new ones. `'x'` survives, `'y'` is overwritten, `'z'` is added.

</details>

---

**P4.4 — Dictionary keys must be hashable**

```python
d = {}
d[[1, 2]] = 'value'
```

<details><summary>Answer</summary>

`TypeError: unhashable type: 'list'`  
Dict keys must be **hashable** (immutable): `int`, `str`, `tuple` are fine.  
`list` is mutable → not hashable → cannot be a key.  
Fix: use a **tuple**: `d[(1, 2)] = 'value'`

</details>

---

**P4.5 — Iterating a dict gives keys**

```python
d = {'a': 1, 'b': 2, 'c': 3}
for item in d:
    print(item)
```

<details><summary>Answer</summary>

```
a
b
c
```
Iterating a dict gives **keys only**.  
Use `.values()` for values, `.items()` for `(key, value)` tuples.

</details>

---

**P4.6 — dict comprehension with conditional**

```python
scores = {'Alice': 85, 'Bob': 42, 'Carol': 91, 'Dave': 58}
passed = {k: v for k, v in scores.items() if v >= 60}
print(passed)
```

<details><summary>Answer</summary>

`{'Alice': 85, 'Carol': 91}`  
Dict comprehension with `if` acts as a filter. Bob (42) and Dave (58) are excluded.

</details>

---

**P4.7 — setdefault vs get**

```python
d = {}
d.setdefault('a', []).append(1)
d.setdefault('a', []).append(2)
d.setdefault('b', []).append(3)
print(d)
```

<details><summary>Answer</summary>

`{'a': [1, 2], 'b': [3]}`  
`setdefault(key, default)` inserts the default if key is missing, then returns the value.  
Second call for `'a'` returns the existing list and appends `2` to it.  
This is the pattern `defaultdict(list)` replaces.

</details>

---

## SQL TRICKY QUESTIONS

---

### Day 1 — WHERE, HAVING, BETWEEN, IN

---

**S1.1 — HAVING without GROUP BY**

```sql
SELECT dept, AVG(salary)
FROM employees
HAVING AVG(salary) > 70000;
```
Is this valid?

<details><summary>Answer</summary>

**Invalid** — `HAVING` requires `GROUP BY` (in standard SQL).  
Without `GROUP BY`, the whole table is one group but `dept` is not aggregated, so this would error.  
Fix: add `GROUP BY dept`.

</details>

---

**S1.2 — NULL in WHERE**

```sql
SELECT * FROM employees WHERE salary != 50000;
```
Do rows where `salary IS NULL` appear in the result?

<details><summary>Answer</summary>

**No.** Comparisons with `NULL` always return `UNKNOWN`, which is treated as `FALSE`.  
`NULL != 50000` → `UNKNOWN` → row excluded.  
To include NULLs: `WHERE salary != 50000 OR salary IS NULL`

</details>

---

**S1.3 — BETWEEN is inclusive**

```sql
SELECT * FROM employees WHERE salary BETWEEN 60000 AND 80000;
```
Are employees with salary exactly 60000 or 80000 included?

<details><summary>Answer</summary>

**Yes.** `BETWEEN a AND b` is equivalent to `>= a AND <= b` — both endpoints are **inclusive**.

</details>

---

**S1.4 — IN with NULL**

```sql
SELECT * FROM employees WHERE dept IN ('Engineering', NULL);
```
Do rows where `dept IS NULL` appear?

<details><summary>Answer</summary>

**No.** `dept = NULL` is `UNKNOWN` — you cannot match NULL with `=` or `IN`.  
To find NULLs: add `OR dept IS NULL` separately.

</details>

---

**S1.5 — WHERE vs HAVING execution order**

Which runs first — `WHERE` or `HAVING`?

<details><summary>Answer</summary>

`WHERE` → `GROUP BY` → `HAVING`  
`WHERE` filters **individual rows** before grouping.  
`HAVING` filters **groups** after aggregation.  
You cannot use aggregate functions in `WHERE`.

</details>

---

### Day 2 — String Functions

---

**S2.1 — TRIM only removes spaces by default**

```sql
SELECT TRIM('  hello  ');   -- result?
SELECT TRIM('xxhelloxx');   -- result?
```

<details><summary>Answer</summary>

```
'hello'
'xxhelloxx'
```
`TRIM()` removes **spaces** by default, not arbitrary characters.  
To remove specific chars: `TRIM('x' FROM 'xxhelloxx')` → `'hello'`

</details>

---

**S2.2 — LIKE is case-sensitive in PostgreSQL**

```sql
SELECT * FROM customers WHERE name LIKE 'alice%';
```
Does this return a row where `name = 'Alice'`?

<details><summary>Answer</summary>

**No** in PostgreSQL — `LIKE` is **case-sensitive**.  
Fix: `LOWER(name) LIKE 'alice%'` or use `ILIKE` (PostgreSQL-specific, case-insensitive).

</details>

---

**S2.3 — CONCAT vs ||**

```sql
SELECT CONCAT('hello', NULL, 'world');
SELECT 'hello' || NULL || 'world';
```
Same result?

<details><summary>Answer</summary>

```
'helloworld'   -- CONCAT ignores NULLs
NULL           -- || propagates NULL
```
`CONCAT` treats NULL as empty string. The `||` operator returns NULL if **any operand is NULL**.  
Use `COALESCE` with `||` to be safe: `'hello' || COALESCE(col, '') || 'world'`

</details>

---

**S2.4 — SUBSTRING index starts at 1**

```sql
SELECT SUBSTRING('abcdef', 2, 3);
```
What is the result?

<details><summary>Answer</summary>

`'bcd'`  
SQL `SUBSTRING(str, start, length)` — `start` is **1-indexed** (not 0 like Python).  
Position 2 = `'b'`, length 3 = `'bcd'`.

</details>

---

### Day 3 — Date & Time Functions

---

**S3.1 — DATE_TRUNC vs DATE_PART**

```sql
SELECT DATE_TRUNC('month', '2024-03-15'::DATE);
SELECT DATE_PART('month', '2024-03-15'::DATE);
```
What does each return?

<details><summary>Answer</summary>

```
2024-03-01 00:00:00   -- DATE_TRUNC: truncates to first of month (returns timestamp)
3                     -- DATE_PART: extracts the month NUMBER
```
`DATE_TRUNC` is used for **grouping by period**. `DATE_PART` extracts a **number** for comparison.

</details>

---

**S3.2 — DATEDIFF direction matters**

```sql
SELECT order_date - ship_date AS diff FROM orders;
-- order_date = '2024-01-10', ship_date = '2024-01-15'
```
What is `diff`?

<details><summary>Answer</summary>

`-5`  
Order was placed before shipping, so `order_date - ship_date` is negative.  
For "days to ship", use `ship_date - order_date` = `5`.

</details>

---

**S3.3 — Filtering by year without DATE_TRUNC**

```sql
-- Two ways to find orders in 2024 — which is sargable (index-friendly)?
-- A:
WHERE EXTRACT(YEAR FROM order_date) = 2024
-- B:
WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01'
```

<details><summary>Answer</summary>

**B is index-friendly (sargable).**  
A wraps the column in a function — this prevents index use on most databases.  
B uses a plain range comparison — the index on `order_date` can be used directly.

</details>

---

### Day 4 — Aggregation

---

**S4.1 — COUNT(*) vs COUNT(column)**

```sql
SELECT COUNT(*), COUNT(salary) FROM employees;
-- Table has 5 rows; 2 rows have NULL salary
```
What are the two counts?

<details><summary>Answer</summary>

```
5    -- COUNT(*) counts all rows regardless of NULLs
3    -- COUNT(salary) counts only non-NULL salary values
```
`COUNT(*)` = total rows. `COUNT(col)` = non-NULL values in that column.

</details>

---

**S4.2 — AVG ignores NULLs**

```sql
-- salaries: 100, 200, NULL, 300
SELECT AVG(salary) FROM employees;
```
What is the result?

<details><summary>Answer</summary>

`200.0` — `(100 + 200 + 300) / 3`  
`AVG` ignores `NULL` — it does NOT treat it as 0.  
If you want NULL treated as 0: `AVG(COALESCE(salary, 0))` = `(100+200+0+300)/4 = 150`

</details>

---

**S4.3 — SUM of an empty group**

```sql
SELECT region, SUM(revenue)
FROM sales
WHERE region = 'Mars'   -- no rows match
GROUP BY region;
```
What is returned?

<details><summary>Answer</summary>

**0 rows** — not a row with `NULL`.  
When `WHERE` filters out all rows before `GROUP BY`, there are no groups to aggregate.  
This is different from a `LEFT JOIN` scenario where the group exists but has no matching rows.

</details>

---

**S4.4 — Can you SELECT a non-aggregated column without GROUP BY?**

```sql
SELECT dept, name, AVG(salary)
FROM employees
GROUP BY dept;
```
Is this valid?

<details><summary>Answer</summary>

**Invalid** in PostgreSQL/standard SQL.  
`name` is not aggregated and not in `GROUP BY` — this errors.  
Fix: either add `name` to `GROUP BY` or remove it from `SELECT`.  
(MySQL allows this but returns an arbitrary `name` value — very dangerous.)

</details>

---

## PYSPARK TRICKY QUESTIONS

---

### Day 1 — filter() / where()

---

**SP1.1 — filter vs where**

```python
df.filter(df.salary > 50000)
df.where(df.salary > 50000)
```
Are these the same?

<details><summary>Answer</summary>

**Yes — identical.** `filter` and `where` are **aliases** in PySpark.  
Both accept a Column expression or a SQL string: `df.filter("salary > 50000")`

</details>

---

**SP1.2 — Column reference styles**

```python
# Which of these are valid ways to reference a column?
df['salary']
df.salary
F.col('salary')
'salary'
```

<details><summary>Answer</summary>

All four work in **different contexts**:
- `df['salary']` and `df.salary` — Column objects from the DataFrame
- `F.col('salary')` — Column object via functions module (safest, works across DataFrames)
- `'salary'` — works inside `select()`, `orderBy()` as a string shorthand  
`F.col()` is preferred in expressions that combine multiple DataFrames (avoids ambiguity).

</details>

---

**SP1.3 — filter with AND / OR — Python `and` doesn't work**

```python
# This is WRONG:
df.filter(df.dept == 'Eng' and df.salary > 70000)

# This is RIGHT:
df.filter((df.dept == 'Eng') & (df.salary > 70000))
```
Why?

<details><summary>Answer</summary>

Python's `and`/`or` operate on **truthiness of objects**, not on Column expressions.  
PySpark Column objects are always truthy as Python objects, so `and` gives incorrect results.  
Use `&` for AND, `|` for OR, `~` for NOT — and **always add parentheses** around each condition.

</details>

---

**SP1.4 — isin vs == for multiple values**

```python
# Which is correct?
df.filter(df.region == ['North', 'South'])
df.filter(df.region.isin(['North', 'South']))
df.filter(df.region.isin('North', 'South'))
```

<details><summary>Answer</summary>

The **second and third** are correct — `isin` accepts a list or `*args`.  
The first (`== ['North', 'South']`) does not work — you can't compare a Column to a list with `==`.

</details>

---

### Day 2 — String Functions

---

**SP2.1 — F.col() is case-sensitive for column names**

```python
df = spark.createDataFrame([('Alice',)], ['Name'])
df.select(F.col('name')).show()   # lowercase 'name'
```
What happens?

<details><summary>Answer</summary>

**AnalysisException** — column `'name'` not found.  
PySpark column names are **case-sensitive by default**.  
The column is `'Name'` (capital N). Use `F.col('Name')` or enable case-insensitivity with `spark.conf.set("spark.sql.caseSensitive", "false")`.

</details>

---

**SP2.2 — regexp_replace replaces ALL matches**

```python
from pyspark.sql import functions as F
df = spark.createDataFrame([('abc-123-def-456',)], ['val'])
df.select(F.regexp_replace('val', r'\d+', 'X')).show()
```
What is the output?

<details><summary>Answer</summary>

`abc-X-def-X`  
`regexp_replace` replaces **all** non-overlapping matches, not just the first.  
This is different from Python's `re.sub` (which also replaces all) vs `re.subn`.

</details>

---

**SP2.3 — split returns an ArrayType**

```python
df = spark.createDataFrame([('a,b,c',)], ['val'])
df.select(F.split('val', ',').alias('parts')).printSchema()
```
What is the dtype of `parts`?

<details><summary>Answer</summary>

`array<string>`  
`F.split()` returns an **ArrayType column**, not a string.  
To access the first element: `F.split('val', ',')[0]`  
To get the size: `F.size(F.split('val', ','))`

</details>

---

### Day 3 — Date Functions

---

**SP3.1 — datediff argument order**

```python
F.datediff(end_date, start_date)
```
Which date is subtracted from which?

<details><summary>Answer</summary>

`datediff(end, start)` = `end - start` in days.  
`F.datediff(F.lit('2024-01-15'), F.lit('2024-01-10'))` → `5`  
If you reverse the order, you get a negative number. Easy to mix up.

</details>

---

**SP3.2 — date_format vs date_trunc**

```python
F.date_format('order_date', 'yyyy-MM')
F.date_trunc('month', 'order_date')
```
What is the return type of each?

<details><summary>Answer</summary>

```
date_format  → StringType  (e.g. '2024-03')
date_trunc   → TimestampType  (e.g. 2024-03-01 00:00:00)
```
Use `date_format` when you need a **string for display or grouping by label**.  
Use `date_trunc` when you need a **date/timestamp for further date arithmetic**.

</details>

---

**SP3.3 — String date columns are not automatically DateType**

```python
df = spark.createDataFrame([('2024-01-15',)], ['order_date'])
df.printSchema()
```
What is the type of `order_date`?

<details><summary>Answer</summary>

`string` — PySpark infers `string` for date-looking strings unless you cast explicitly.  
`F.datediff` and `F.date_trunc` will **fail** on a string column.  
Fix: `F.to_date(F.col('order_date'), 'yyyy-MM-dd')` to cast to `DateType`.

</details>

---

### Day 4 — Aggregations

---

**SP4.1 — groupBy().count() vs agg(F.count('*'))**

```python
df.groupBy('dept').count()
df.groupBy('dept').agg(F.count('*').alias('cnt'))
```
Same result?

<details><summary>Answer</summary>

**Yes, same result.**  
`.count()` is a shorthand that calls `COUNT(*)` internally.  
`.agg(F.count('*'))` does the same but lets you rename the column and combine with other aggregates in one pass.

</details>

---

**SP4.2 — F.count('col') vs F.count('*')**

```python
# Column 'salary' has some NULLs
df.groupBy('dept').agg(
    F.count('*').alias('total_rows'),
    F.count('salary').alias('non_null_salary')
)
```
When do these differ?

<details><summary>Answer</summary>

They differ when the column has **NULL values**.  
`F.count('*')` counts all rows. `F.count('salary')` counts only non-NULL values.  
Same as SQL `COUNT(*) vs COUNT(column)`.

</details>

---

**SP4.3 — agg result column name**

```python
df.groupBy('region').agg(F.sum('revenue'))
```
What is the column name of the aggregated result?

<details><summary>Answer</summary>

`sum(revenue)` — PySpark auto-names it `function(column)`.  
This is awkward for downstream code. Always use `.alias()`:  
`F.sum('revenue').alias('total_revenue')`

</details>

---

**SP4.4 — F.round vs Python round**

```python
from pyspark.sql import functions as F
df.select(F.round(F.col('revenue'), 2))
```
Can you use Python's built-in `round()` here instead?

<details><summary>Answer</summary>

**No.** Python's `round()` works on **Python scalars**, not Spark Column objects.  
In a Spark expression you must use `F.round(col, scale)`.  
Python's `round` inside a `udf` would work, but UDFs are slow — prefer `F.round`.

</details>

---

**SP4.5 — Lazy evaluation: when does the job actually run?**

```python
df2 = df.filter(df.salary > 50000)
df3 = df2.groupBy('dept').agg(F.sum('salary'))
# Has anything executed yet?
df3.show()
# Now what happens?
```

<details><summary>Answer</summary>

**Nothing executes** until `show()` (or `collect()`, `write`, `count()`).  
PySpark builds a **logical plan** (DAG) on every transformation.  
`show()` is an **action** — it triggers the actual Spark job.  
This is the core of Spark's **lazy evaluation** model.

</details>

---

## QUICK REFERENCE — The Most Common Gotchas

| Gotcha | Python | SQL | PySpark |
|--------|--------|-----|---------|
| Assignment is not a copy | `b = a` shares list | — | `df2 = df` shares reference (but safe — DataFrames are immutable) |
| NULLs break comparisons | `None == None` is `True` | `NULL = NULL` is `UNKNOWN` | `df.filter(col.isNull())` not `col == None` |
| Iterators exhaust | `map`, `zip`, `filter`, `enumerate` | — | use `.cache()` if reusing a DataFrame |
| Index | 0-based | 1-based (SUBSTRING) | 0-based for array elements |
| Case sensitivity | strings are case-sensitive | LIKE is case-sensitive in PG | column names are case-sensitive |
| In-place vs new object | `sort()` in-place, `sorted()` new | — | all transforms return new DataFrames |
| NULLs in aggregation | `sum([1,None,2])` errors | `AVG` ignores NULLs | `F.sum` ignores NULLs |
