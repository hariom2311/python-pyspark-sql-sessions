# Day 6 — Solutions: Python · SQL · PySpark

> **Python:** API Response Handling — real APIs, pagination, throttling, retry + exponential backoff  
> **SQL:** Window Functions Part 1 (ROW_NUMBER, RANK, DENSE_RANK)  
> **PySpark:** Same — using `Window.partitionBy().orderBy()` + `rank()`, `dense_rank()`
>
> **Real APIs used (free, no key):** JSONPlaceholder · Open-Meteo · REST Countries

---

## PYTHON

### Shared Helper — get_with_retry (used by all 3 questions)

```python
import requests, time, random

def get_with_retry(url, params=None, max_retries=4, base_delay=1.0):
    """
    GET with exponential backoff.
    - 429: respect Retry-After header, then retry
    - 5xx: backoff + jitter, then retry
    - 4xx: raise immediately (client error — our bug, not transient)
    - Timeout/ConnectionError: backoff, then retry
    """
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, params=params, timeout=10)

            if resp.status_code == 429:
                wait = float(resp.headers.get('Retry-After', base_delay * (2 ** attempt)))
                print(f'[429] Rate limited. Waiting {wait:.1f}s (attempt {attempt+1})')
                time.sleep(wait)
                continue

            if resp.status_code >= 500:
                wait = base_delay * (2 ** attempt) + random.uniform(0, 0.5)  # jitter
                print(f'[{resp.status_code}] Server error. Retrying in {wait:.1f}s')
                time.sleep(wait)
                continue

            resp.raise_for_status()   # 4xx → immediate failure
            return resp.json()

        except requests.exceptions.Timeout:
            time.sleep(base_delay * (2 ** attempt))
        except requests.exceptions.ConnectionError:
            time.sleep(base_delay * (2 ** attempt))

    raise RuntimeError(f'All {max_retries} retries exhausted for {url}')
```

**Backoff schedule (`base_delay=1`):** attempt 0 → 1s · attempt 1 → 2s · attempt 2 → 4s · attempt 3 → 8s  
**Jitter** (`random.uniform(0, 0.5)`) prevents thundering herd when many clients retry simultaneously.

---

### Q1 (Easy) — Fetch All Posts with Pagination + Throttling

**API:** `GET https://jsonplaceholder.typicode.com/posts?_page=N&_limit=10`

```python
def fetch_all_posts(page_size=10, delay=0.3):
    all_posts, page = [], 1
    while True:
        batch = get_with_retry(
            'https://jsonplaceholder.typicode.com/posts',
            params={'_page': page, '_limit': page_size},
        )
        if not batch:          # empty page → no more data
            break
        all_posts.extend(batch)
        print(f'Page {page}: +{len(batch)} posts (total: {len(all_posts)})')
        page += 1
        time.sleep(delay)      # throttle: max 1/delay requests per second
    return all_posts

posts = fetch_all_posts(page_size=10, delay=0.3)
# → 100 posts total across 10 pages
```

**Key concepts:**
- `if not batch: break` — empty list signals last page; don't check `len < page_size` (last page may still be full)
- `list.extend(batch)` not `list.append(batch)` — flattens page into accumulator
- `time.sleep(delay)` between pages — respects API rate limits even when no 429 is returned
- Always use `get_with_retry()` not bare `requests.get()` in production

---

### Q2 (Medium) — Weather Batch with Retry + Error Isolation

**API:** `GET https://api.open-meteo.com/v1/forecast` (no key needed)

```python
WEATHER_URL = 'https://api.open-meteo.com/v1/forecast'

def fetch_weather_batch(cities, delay=0.5):
    records, failed = [], []

    for city in cities:
        try:
            data = get_with_retry(
                WEATHER_URL,
                params={
                    'latitude':  city['lat'],
                    'longitude': city['lon'],
                    'current':   ['temperature_2m', 'wind_speed_10m', 'relative_humidity_2m'],
                    'timezone':  'auto',
                    'forecast_days': 1,
                },
            )
            current = data['current']
            records.append({
                'city':         city['name'],
                'temp_c':       current.get('temperature_2m'),
                'wind_kmh':     current.get('wind_speed_10m'),
                'humidity_pct': current.get('relative_humidity_2m'),
                'fetched_at':   current.get('time'),
            })
        except Exception as e:
            # Isolate failures — one bad city must not crash the whole batch
            failed.append({'city': city['name'], 'error': str(e)})

        time.sleep(delay)   # throttle between cities

    return records, failed
```

**Key concepts:**
- `try/except Exception` around each city — isolates failures; one bad record never kills the batch
- Returns `(records, failed)` — both lists always returned; failed records go to dead-letter storage
- `current.get('temperature_2m')` — safe access; field might be absent in some edge cases
- `time.sleep(delay)` runs even on failure — throttle applies to all requests including retried ones

---

### Q3 (Medium) — Paginated Posts Enriched with User Data (Cache Pattern)

**APIs:** JSONPlaceholder posts + users

```python
POSTS_URL = 'https://jsonplaceholder.typicode.com/posts'
USERS_URL = 'https://jsonplaceholder.typicode.com/users'

def fetch_enriched_posts(num_pages=2, page_size=10, delay=0.3):
    user_cache = {}    # {user_id: user_dict} — fetch each user at most once
    enriched   = []

    for page in range(1, num_pages + 1):
        posts = get_with_retry(POSTS_URL, params={'_page': page, '_limit': page_size})
        time.sleep(delay)

        for post in posts:
            uid = post['userId']
            if uid not in user_cache:
                user_cache[uid] = get_with_retry(f'{USERS_URL}/{uid}')
                time.sleep(delay)   # throttle user lookups too (cache misses only)

            user = user_cache[uid]
            enriched.append({
                'post_id':      post['id'],
                'title':        post['title'],
                'user_id':      uid,
                'user_name':    user.get('name', 'N/A'),
                'user_email':   user.get('email', 'N/A'),
                # Nested safe access — .get('company', {}).get('name') handles missing company
                'user_company': user.get('company', {}).get('name', 'N/A'),
                'user_city':    user.get('address', {}).get('city', 'N/A'),
            })

    return enriched
```

**Key concepts:**
- `user_cache = {}` — dict keyed by `user_id`; avoids re-fetching the same user for every post
- `user.get('company', {}).get('name', 'N/A')` — safe double-nested access; `{}` default means second `.get()` never raises AttributeError
- Throttle only on cache misses — `time.sleep(delay)` inside `if uid not in user_cache` block
- JSONPlaceholder has 10 users, 100 posts — cache should have ≤10 entries regardless of how many posts are fetched

---

## SQL

> **Data:** `d6w_sales(emp_id, emp_name, region, month, revenue)`  
> **Tie designed:** Bob & Carol both have 4200 in North/month1; Frank & Grace both have 5500 in South/month1

### Q1 (Easy) — Rank Employees by Revenue Within Each Region

```sql
SELECT emp_id,
       emp_name,
       region,
       month,
       revenue,
       RANK() OVER (PARTITION BY region ORDER BY revenue DESC) AS revenue_rank
FROM   d6w_sales
ORDER  BY region, revenue_rank;
```

**Note:** `PARTITION BY region` only (not `region, month`) means the rank is across ALL months for that region. Alice's month2 revenue of 5300 beats her own month1 revenue of 5000 — she ranks #1.

---

### Q2 (Medium) — Top 2 per Region (Ties Both Included)

```sql
WITH ranked AS (
    SELECT emp_id, emp_name, region, month, revenue,
           DENSE_RANK() OVER (PARTITION BY region ORDER BY revenue DESC) AS drnk
    FROM   d6w_sales
    WHERE  month = 1
)
SELECT * FROM ranked
WHERE  drnk <= 2
ORDER  BY region, drnk;
-- 6 rows: Alice+Bob+Carol (North), Eve+Frank+Grace (South)
```

**Why DENSE_RANK, not RANK?**  
With RANK: Bob and Carol both get rank 2, but Dave gets rank 4 (gap at 3).  
`WHERE rnk <= 2` includes Bob and Carol. But if ties push someone to rank 3 and there's no 2, `dense_rank <= 2` is cleaner and more predictable for top-N.

With DENSE_RANK: Bob and Carol both get rank 2, Dave gets rank 3. `WHERE drnk <= 2` is clean.

---

### Q3 (Medium) — Employees Who Ranked #1 in Any Region for Any Month

```sql
WITH ranked AS (
    SELECT emp_id, emp_name, region, month, revenue,
           RANK() OVER (PARTITION BY region, month ORDER BY revenue DESC) AS rnk
    FROM   d6w_sales
)
SELECT emp_id, emp_name, region, month, revenue
FROM   ranked
WHERE  rnk = 1
ORDER  BY region, month;
-- Alice: North/1 and North/2
-- Eve: South/1
-- Frank: South/2
```

**Key:** `PARTITION BY region, month` — the window resets for every (region, month) combination.  
4 rows total. If there were a tie for #1 in any window, both would appear with rank=1.

---

## PYSPARK

### Q1 (Easy) — Rank by Revenue Within Region

```python
from pyspark.sql import Window, functions as F

w = Window.partitionBy('region').orderBy(F.desc('revenue'))

df_q1 = (
    df_sales
    .withColumn('revenue_rank', F.rank().over(w))
    .orderBy('region', 'revenue_rank')
)
df_q1.show()
```

**Assertion checks:**
- Alice month2 (5300) → `revenue_rank == 1` in North
- Bob and Carol both 4200 in month1 → same `revenue_rank`

---

### Q2 (Medium) — Top 2 per Region (Dense Rank, Month 1 Only)

```python
w = Window.partitionBy('region').orderBy(F.desc('revenue'))

df_q2 = (
    df_sales
    .filter(F.col('month') == 1)            # filter BEFORE window — window sees only month1 rows
    .withColumn('drnk', F.dense_rank().over(w))
    .filter(F.col('drnk') <= 2)
    .drop('drnk')
    .orderBy('region', F.desc('revenue'))
)
df_q2.show()
# 6 rows: 3 per region (ties at rank 2 both included)
```

**Assertion checks:**
- `df_q2.count() == 6`
- Dave not in result; Bob AND Carol both in result

---

### Q3 (Medium) — Ranked #1 in Any Region for Any Month

```python
w = Window.partitionBy('region', 'month').orderBy(F.desc('revenue'))

df_q3 = (
    df_sales
    .withColumn('rnk', F.rank().over(w))
    .filter(F.col('rnk') == 1)
    .select('emp_id', 'emp_name', 'region', 'month', 'revenue')
    .distinct()
    .orderBy('region', 'month')
)
df_q3.show()
# 4 rows: Alice(N/1), Alice(N/2), Eve(S/1), Frank(S/2)
```

**Assertion checks:**
- `count() == 4`
- `{(emp_name, region, month)}` == `{('Alice','North',1), ('Alice','North',2), ('Eve','South',1), ('Frank','South',2)}`

---

## Concepts at a Glance

| Concept | Python | SQL | PySpark |
|---------|--------|-----|---------|
| Load JSON from file | `json.load(f)` | — | `spark.read.json(path)` |
| Parse JSON string | `json.loads(s)` | — | — |
| Paginate | `yield records[i:i+n]` | `LIMIT n OFFSET i` | `.limit(n)` |
| Required key check | `all(k in d for k in required)` | `IS NOT NULL` | `.filter(F.col('k').isNotNull())` |
| Unique rank | — | `ROW_NUMBER()` | `F.row_number().over(w)` |
| Rank with gaps | — | `RANK()` | `F.rank().over(w)` |
| Rank no gaps | — | `DENSE_RANK()` | `F.dense_rank().over(w)` |
| Partition window | — | `PARTITION BY col` | `Window.partitionBy('col')` |
| Top-N per group | — | CTE + `WHERE drnk <= N` | `.withColumn().filter()` |
| Can't filter directly | — | Window fn not in `WHERE` | Window fn not in `.agg()` |

---

## Also Created: Day 6 Extra (HashSet / ROLLUP / cube)

The original Day 6 content (HashSet & Set Operations, GROUP BY/ROLLUP/GROUPING SETS, PySpark groupBy/rollup/cube) was moved to:
- `python/day06extra_hashset_set_operations/`
- `sql/day06extra_groupby_rollup_groupingsets/`
- `pyspark/day06extra_groupby_rollup_cube/`

These map to **Day 6 bonus** content — covered in the roadmap as part of Day 6's original curriculum. Now reclassified as extra practice.
