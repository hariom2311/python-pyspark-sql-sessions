# Day 3 — Python: Array & List Operations

> **Roadmap Day:** 3 · **Date:** Wednesday, June 17, 2026  
> **Study Window:** 9 PM – 11 PM  
> **Interview Level:** Easy → Medium

---

## 1. Lists Are Mutable Ordered Sequences

A Python `list` is a **mutable**, **ordered** sequence of any types. Unlike strings, lists can be changed in-place.

```python
nums = [3, 1, 4, 1, 5, 9, 2, 6]

nums.append(7)        # add to end — O(1)
nums.insert(0, 0)     # insert at index 0 — O(n)
nums.pop()            # remove + return last — O(1)
nums.pop(0)           # remove + return at index — O(n)
nums.remove(1)        # remove first occurrence of value — O(n)
```

**Key mental model:** Random access `O(1)`, append/pop-from-end `O(1)`, insert/remove-from-middle `O(n)`.

---

## 2. Sorting

```python
nums = [3, 1, 4, 1, 5, 9, 2, 6]

# sorted() — returns new list, original unchanged
asc  = sorted(nums)               # [1, 1, 2, 3, 4, 5, 6, 9]
desc = sorted(nums, reverse=True) # [9, 6, 5, 4, 3, 2, 1, 1]

# list.sort() — in-place, returns None
nums.sort()           # mutates nums
nums.sort(reverse=True)

# Sort by key
employees = [
    {"name": "Alice", "salary": 95000},
    {"name": "Bob",   "salary": 72000},
    {"name": "Carol", "salary": 85000},
]
employees.sort(key=lambda e: e["salary"], reverse=True)
# [Alice 95000, Carol 85000, Bob 72000]
```

**Critical distinction:** `sorted()` is safe in loops and returns a new list. `list.sort()` mutates — never use it if you still need the original order.

---

## 3. List Comprehensions

```python
# Basic: [expression for item in iterable if condition]
squares = [x**2 for x in range(1, 6)]             # [1, 4, 9, 16, 25]
evens   = [x for x in range(10) if x % 2 == 0]    # [0, 2, 4, 6, 8]

# DE use case: clean a list of values
raw = ["  Alice ", " BOB  ", "carol  ", None, "  DAVE"]
clean = [s.strip().title() for s in raw if s is not None]
# ['Alice', 'Bob', 'Carol', 'Dave']

# Nested comprehension — flatten a list of lists
batches = [[1, 2, 3], [4, 5], [6, 7, 8, 9]]
flat    = [x for batch in batches for x in batch]
# [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

---

## 4. Slicing

```python
nums = [10, 20, 30, 40, 50, 60, 70]

print(nums[1:4])     # [20, 30, 40]   — start inclusive, stop exclusive
print(nums[:3])      # [10, 20, 30]   — first 3
print(nums[-3:])     # [50, 60, 70]   — last 3
print(nums[::2])     # [10, 30, 50, 70] — every 2nd
print(nums[::-1])    # [70, 60, 50, 40, 30, 20, 10] — reversed

# Slicing is a COPY — original unchanged
copy = nums[:]       # full shallow copy
```

---

## 5. Common List Methods

| Method | Returns | Mutates? | Complexity |
|--------|---------|----------|------------|
| `append(x)` | None | Yes | O(1) |
| `extend(iter)` | None | Yes | O(k) |
| `insert(i, x)` | None | Yes | O(n) |
| `pop(i=-1)` | item | Yes | O(1) tail / O(n) mid |
| `remove(x)` | None | Yes | O(n) |
| `index(x)` | int | No | O(n) |
| `count(x)` | int | No | O(n) |
| `reverse()` | None | Yes | O(n) |
| `copy()` | list | No | O(n) |
| `clear()` | None | Yes | O(n) |

```python
a = [1, 2, 3]
b = [4, 5, 6]

a.extend(b)      # a = [1, 2, 3, 4, 5, 6]
a + b            # returns new list — does NOT mutate a
```

---

## 6. Two-Pointer Pattern

Used for: finding pairs, checking sorted conditions, removing duplicates in sorted arrays.

```python
# Find two numbers that sum to target
def two_sum_sorted(nums, target):
    left, right = 0, len(nums) - 1
    while left < right:
        s = nums[left] + nums[right]
        if s == target:
            return (nums[left], nums[right])
        elif s < target:
            left += 1
        else:
            right -= 1
    return None

nums = sorted([3, 7, 1, 8, 2, 5])  # [1, 2, 3, 5, 7, 8]
print(two_sum_sorted(nums, 9))       # (1, 8)
```

---

## 7. Stack Pattern (List as Stack)

Python list can act as a stack: `append()` = push, `pop()` = pop.

```python
stack = []
stack.append(1)   # push
stack.append(2)
stack.append(3)
top = stack.pop() # pop → 3

# Classic stack problem: matching brackets
def is_balanced(s):
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    for ch in s:
        if ch in '([{':
            stack.append(ch)
        elif ch in ')]}':
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
    return len(stack) == 0

print(is_balanced("({[]})"))  # True
print(is_balanced("({[})"))   # False
```

---

## 8. Finding Second Highest Without Sorting Multiple Times

```python
def second_highest(salaries):
    # Sort once descending — O(n log n)
    unique = sorted(set(salaries), reverse=True)
    return unique[1] if len(unique) >= 2 else None

salaries = [95000, 72000, 85000, 95000, 60000, 85000]
print(second_highest(salaries))   # 85000
```

**Alternative — single pass O(n):**
```python
def second_highest_linear(nums):
    first = second = float('-inf')
    for n in nums:
        if n > first:
            second = first
            first  = n
        elif n > second and n != first:
            second = n
    return second if second != float('-inf') else None
```

---

## 9. Deduplicate Preserving Insertion Order

```python
# dict.fromkeys preserves order (Python 3.7+)
def deduplicate(lst):
    return list(dict.fromkeys(lst))

ids = [101, 203, 101, 305, 203, 101, 407]
print(deduplicate(ids))   # [101, 203, 305, 407]

# Why not set()? Sets don't preserve order.
print(list(set(ids)))     # order unpredictable
```

---

## 10. Daily Temperatures — Stack Pattern (Medium)

```python
def days_until_warmer(temperatures):
    """For each day, how many days until a warmer temperature?"""
    n      = len(temperatures)
    result = [0] * n
    stack  = []    # stores indices of days waiting for a warmer day

    for i, temp in enumerate(temperatures):
        # while stack has days that are colder than today
        while stack and temperatures[stack[-1]] < temp:
            prev_day         = stack.pop()
            result[prev_day] = i - prev_day
        stack.append(i)

    return result

temps = [73, 74, 75, 71, 69, 72, 76, 73]
print(days_until_warmer(temps))
# [1, 1, 4, 2, 1, 1, 0, 0]
```

**Stack mental model:** Push index when you don't yet know the answer. Pop when you find the warmer day.

---

## 11. Day 3 Problems — Solutions

### Problem 1 (Easy) — Second highest salary
```python
salaries = [95000, 72000, 85000, 95000, 60000, 85000]
unique   = sorted(set(salaries), reverse=True)
print(unique[1])   # 85000
```

### Problem 2 (Easy) — Deduplicate preserving order
```python
ids = [101, 203, 101, 305, 203, 101, 407]
clean = list(dict.fromkeys(ids))
print(clean)   # [101, 203, 305, 407]
```

### Problem 3 (Medium) — Days until warmer
```python
def days_until_warmer(temps):
    result = [0] * len(temps)
    stack  = []
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            result[j] = i - j
        stack.append(i)
    return result

temps = [73, 74, 75, 71, 69, 72, 76, 73]
print(days_until_warmer(temps))  # [1, 1, 4, 2, 1, 1, 0, 0]
```

---

## 12. Interview Checklist

| Question | Answer |
|----------|--------|
| `list.sort()` vs `sorted()`? | `sort()` mutates in-place, returns None. `sorted()` returns new list, original unchanged. |
| How to deduplicate preserving order? | `list(dict.fromkeys(lst))` — works in Python 3.7+ |
| Why not `set()` for dedup? | `set` doesn't preserve insertion order |
| List slicing creates a copy? | Yes — `nums[1:4]` is a shallow copy of that range |
| `append` vs `extend`? | `append(x)` adds x as a single element; `extend(iter)` unpacks and adds all elements |
| Stack in Python? | Use list: `append()` = push, `pop()` = pop from end |
| Second highest salary — best approach? | `sorted(set(nums), reverse=True)[1]` for simplicity; single-pass O(n) for large data |

---

## 13. Quick Reference

```python
# Create
lst = [1, 2, 3]
lst = list(range(1, 6))      # [1, 2, 3, 4, 5]
lst = [0] * 5                # [0, 0, 0, 0, 0]

# Add / Remove
lst.append(x)                # end — O(1)
lst.extend([x, y])           # extend with iterable
lst.insert(i, x)             # at index — O(n)
lst.pop()                    # last — O(1)
lst.pop(i)                   # at index — O(n)
lst.remove(x)                # first match — O(n)

# Sort
sorted(lst)                  # new list asc
sorted(lst, reverse=True)    # new list desc
sorted(lst, key=lambda x: x["salary"])

# Slice
lst[1:4]   lst[:3]   lst[-3:]   lst[::-1]

# Comprehension
[f(x) for x in lst if cond(x)]
[x for row in matrix for x in row]   # flatten

# Dedup preserving order
list(dict.fromkeys(lst))

# Stack
stack = []
stack.append(x)   # push
stack.pop()       # pop

# Second highest
sorted(set(lst), reverse=True)[1]

# Two pointer (sorted input)
l, r = 0, len(lst) - 1
while l < r: ...
```
