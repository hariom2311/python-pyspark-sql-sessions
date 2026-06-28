# Day 6 — Python: HashSet & Set Operations

> **Roadmap Day:** 6 · **Date:** Saturday, June 21, 2026  
> **Study Window:** 9 PM – 11 PM  
> **Interview Level:** Easy → Medium

---

## 1. Why Sets Matter for Data Engineers

Deduplication, membership testing, finding differences between two lists of IDs — all O(1) per lookup with a set vs O(n) with a list. Common in pipeline logic: "which records are new?", "which IDs appear in both tables?", "what changed?"

---

## 2. Set Basics

```python
# Create
s = {1, 2, 3}
s = set([1, 2, 2, 3])     # deduplicates → {1, 2, 3}
s = set()                  # empty set — NOT {} (that's a dict)

# Add / Remove
s.add(4)
s.remove(4)                # KeyError if missing
s.discard(99)              # safe — no error if missing

# Membership — O(1)
3 in s                     # True
99 not in s                # True
```

---

## 3. The Four Set Operations

```python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

# Union — all elements from both
a | b                      # {1, 2, 3, 4, 5, 6}
a.union(b)

# Intersection — elements in BOTH
a & b                      # {3, 4}
a.intersection(b)

# Difference — in A but NOT in B
a - b                      # {1, 2}
a.difference(b)

# Symmetric difference — in one but NOT both
a ^ b                      # {1, 2, 5, 6}
a.symmetric_difference(b)
```

---

## 4. Set from a List — Deduplication

```python
product_ids = ['P001', 'P002', 'P001', 'P003', 'P002']
unique_ids = set(product_ids)          # {'P001', 'P002', 'P003'}

# Preserve insertion order (Python 3.7+)
seen = set()
deduped = []
for pid in product_ids:
    if pid not in seen:
        seen.add(pid)
        deduped.append(pid)
# ['P001', 'P002', 'P003'] — original order preserved
```

---

## 5. First Non-Repeating Character Pattern

```python
def first_non_repeating(s):
    from collections import Counter
    counts = Counter(s)
    for ch in s:
        if counts[ch] == 1:
            return ch
    return None

# Alternative using dict + set (two-pass)
def first_non_repeating_v2(s):
    seen_once = set()
    seen_more = set()
    for ch in s:
        if ch in seen_more:
            continue
        if ch in seen_once:
            seen_once.discard(ch)
            seen_more.add(ch)
        else:
            seen_once.add(ch)
    # Return first char in original string that is still in seen_once
    for ch in s:
        if ch in seen_once:
            return ch
    return None
```

---

## 6. Set for Membership Testing (O(1) vs O(n))

```python
# List lookup — O(n) per check
valid_statuses_list = ['completed', 'pending', 'cancelled']
'completed' in valid_statuses_list    # scans entire list

# Set lookup — O(1) per check
valid_statuses = {'completed', 'pending', 'cancelled'}
'completed' in valid_statuses         # hash lookup, instant

# Rule: if you are checking membership more than once, convert to set first
```

---

## 7. Common DE Patterns with Sets

```python
# Find new records (in current but not in previous)
previous_ids = {'C001', 'C002', 'C003'}
current_ids  = {'C002', 'C003', 'C004', 'C005'}
new_ids = current_ids - previous_ids       # {'C004', 'C005'}

# Find deleted records
deleted_ids = previous_ids - current_ids   # {'C001'}

# Find records in both (intersection check)
both = previous_ids & current_ids          # {'C002', 'C003'}

# Dedup a pipeline output
raw_records = [('C001', 'Alice'), ('C001', 'Alice'), ('C002', 'Bob')]
seen = set()
clean = []
for r in raw_records:
    if r[0] not in seen:
        seen.add(r[0])
        clean.append(r)
```

---

## 8. Day 6 Problem Solutions

### Q1 — Products in A but not B
```python
def products_only_in_a(list_a, list_b):
    return set(list_a) - set(list_b)

# Usage
a = ['P001', 'P002', 'P003', 'P004']
b = ['P003', 'P004', 'P005']
print(products_only_in_a(a, b))   # {'P001', 'P002'}
```

### Q2 — First non-repeating character
```python
from collections import Counter

def first_non_repeating(s):
    counts = Counter(s)
    for ch in s:
        if counts[ch] == 1:
            return ch
    return None

print(first_non_repeating('aabbcde'))  # 'c'
print(first_non_repeating('aabb'))     # None
```

### Q3 — Customer IDs in both refunds and purchases
```python
def customers_in_both(refunds, purchases):
    return set(refunds) & set(purchases)

refunds   = ['C001', 'C003', 'C005', 'C007']
purchases = ['C001', 'C002', 'C005', 'C008']
print(customers_in_both(refunds, purchases))  # {'C001', 'C005'}
```

---

## 9. Interview Checklist

- [ ] Create a set from a list — deduplication in one step
- [ ] `set()` for empty set — NOT `{}`
- [ ] Difference (`-`), intersection (`&`), union (`|`), symmetric difference (`^`)
- [ ] `.discard()` vs `.remove()` — discard is safe, remove raises KeyError
- [ ] Membership check is O(1) for set, O(n) for list
- [ ] Preserve insertion order while deduplicating — `seen` set + list append

---

## 10. Quick Reference

| Operation | Syntax | Result |
|-----------|--------|--------|
| Union | `a \| b` or `a.union(b)` | All elements from both |
| Intersection | `a & b` or `a.intersection(b)` | Only in both |
| Difference | `a - b` or `a.difference(b)` | In A, not in B |
| Symmetric diff | `a ^ b` | In one but not both |
| Membership | `x in s` | O(1) |
| Add element | `s.add(x)` | — |
| Remove (safe) | `s.discard(x)` | No error if missing |
| Remove (strict) | `s.remove(x)` | KeyError if missing |
| Deduplicate list | `set(lst)` | Loses order |
| Deduplicate (ordered) | `seen = set(); [x for x in lst if not (seen.add(x) or x in seen)]` | Preserves order |
