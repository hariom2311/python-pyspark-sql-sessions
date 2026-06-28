# Day 6 — Python: API Response Handling

> **Roadmap Day:** 6  
> **Topics:** Real API calls · `requests` · Pagination · Throttling · Retry + backoff · Error handling  
> **APIs used:** Open-Meteo (weather, free, no key) · JSONPlaceholder (posts/users, free) · REST Countries (free)  
> **Interview Level:** Easy → Medium

---

## 1. Why This Matters for Data Engineers

Every real pipeline eventually hits a REST API — weather data, payments, CRM records, inventory feeds. APIs have three hard constraints:

| Problem | Symptom | Solution |
|---------|---------|---------|
| Pagination | Only 100 records returned, 10 000 exist | Loop over pages until `next` is None |
| Rate limiting | HTTP 429 Too Many Requests | `time.sleep()` between calls / respect `Retry-After` header |
| Transient failures | HTTP 500, timeout, connection drop | Exponential backoff + retry |

---

## 2. The `requests` Library Basics

```python
import requests

resp = requests.get('https://jsonplaceholder.typicode.com/posts', params={'userId': 1})

print(resp.status_code)   # 200
print(resp.headers['Content-Type'])
data = resp.json()         # parse JSON body → list or dict
```

**Always check status before consuming:**
```python
resp.raise_for_status()   # raises requests.HTTPError for 4xx/5xx
```

---

## 3. Pagination Patterns

### 3a. Page-number pagination (most common)

```python
# JSONPlaceholder: GET /posts?_page=1&_limit=10
import requests, time

def fetch_all_posts(page_size=10, delay=0.5):
    all_posts, page = [], 1
    while True:
        resp = requests.get(
            'https://jsonplaceholder.typicode.com/posts',
            params={'_page': page, '_limit': page_size},
            timeout=10,
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:          # empty page = done
            break
        all_posts.extend(batch)
        page += 1
        time.sleep(delay)      # throttle between pages
    return all_posts
```

### 3b. Cursor / next-URL pagination

```python
# Some APIs return the next page URL in the response body or Link header
def fetch_cursor_paginated(start_url):
    records, url = [], start_url
    while url:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        records.extend(data['results'])
        url = data.get('next')   # None when done
    return records
```

### 3c. Generator pattern — lazy pagination

```python
def paginate_posts(page_size=10, delay=0.3):
    """Yields one page at a time — caller decides when to stop."""
    page = 1
    while True:
        resp = requests.get(
            'https://jsonplaceholder.typicode.com/posts',
            params={'_page': page, '_limit': page_size},
            timeout=10,
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            return
        yield batch
        page += 1
        time.sleep(delay)

# Collect first 3 pages only
records = []
for i, page in enumerate(paginate_posts(page_size=5)):
    records.extend(page)
    if i >= 2:          # stop after page 3
        break
```

---

## 4. Throttling — Rate Limit Compliance

Rate limits are expressed as **N requests per second/minute/hour**. Two strategies:

### 4a. Fixed sleep between requests

```python
import time

RATE_LIMIT_DELAY = 1.0   # 1 second → max 1 req/sec

for city in cities:
    resp = requests.get(url, params={'city': city}, timeout=10)
    data = resp.json()
    time.sleep(RATE_LIMIT_DELAY)
```

### 4b. Respect the Retry-After header (HTTP 429)

```python
def get_with_throttle(url, params=None, max_retries=3):
    for attempt in range(max_retries):
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 429:
            wait = int(resp.headers.get('Retry-After', 5))
            print(f'Rate limited. Waiting {wait}s ...')
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return resp.json()
    raise RuntimeError('Max retries exceeded (rate limit)')
```

---

## 5. Retry Logic with Exponential Backoff

**Exponential backoff:** after each failure, wait 2^attempt seconds before retrying.  
This avoids hammering a struggling server.

```python
import requests, time, random

def get_with_retry(url, params=None, max_retries=4, base_delay=1.0):
    """
    Retries on 429 and 5xx with exponential backoff + jitter.
    Raises immediately on 4xx (except 429) — those are our fault.
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
                wait = base_delay * (2 ** attempt) + random.uniform(0, 0.5)
                print(f'[{resp.status_code}] Server error. Retrying in {wait:.1f}s (attempt {attempt+1})')
                time.sleep(wait)
                continue

            resp.raise_for_status()    # 4xx → immediate failure (our bug)
            return resp.json()

        except requests.exceptions.Timeout:
            wait = base_delay * (2 ** attempt)
            print(f'[Timeout] Retrying in {wait:.1f}s (attempt {attempt+1})')
            time.sleep(wait)

        except requests.exceptions.ConnectionError as e:
            wait = base_delay * (2 ** attempt)
            print(f'[ConnectionError] {e}. Retrying in {wait:.1f}s')
            time.sleep(wait)

    raise RuntimeError(f'All {max_retries} retries exhausted for {url}')
```

**Backoff schedule with `base_delay=1`:**
| Attempt | Wait |
|---------|------|
| 0 | 1s |
| 1 | 2s |
| 2 | 4s |
| 3 | 8s |

---

## 6. Real API Examples

### Open-Meteo (weather, no key needed)

```python
# GET https://api.open-meteo.com/v1/forecast
# params: latitude, longitude, daily, timezone
resp = requests.get(
    'https://api.open-meteo.com/v1/forecast',
    params={
        'latitude':  28.6139,
        'longitude': 77.2090,
        'daily':     ['temperature_2m_max', 'precipitation_sum'],
        'timezone':  'Asia/Kolkata',
        'forecast_days': 7,
    },
    timeout=10,
)
data = resp.json()
# data['daily']['time']                   → list of dates
# data['daily']['temperature_2m_max']     → list of max temps
```

### JSONPlaceholder (fake REST, no key)

```python
# Paginated posts
resp = requests.get(
    'https://jsonplaceholder.typicode.com/posts',
    params={'_page': 1, '_limit': 10},
    timeout=10,
)
posts = resp.json()   # list of 10 post dicts

# Nested: fetch user for each post
user_resp = requests.get(
    f"https://jsonplaceholder.typicode.com/users/{posts[0]['userId']}",
    timeout=10,
)
user = user_resp.json()
```

### REST Countries (country info, no key)

```python
# All countries
resp = requests.get('https://restcountries.com/v3.1/all', timeout=15)
countries = resp.json()

# Flatten: name, region, population, capital
flat = [
    {
        'name':       c['name']['common'],
        'region':     c.get('region', 'Unknown'),
        'population': c.get('population', 0),
        'capital':    c.get('capital', ['N/A'])[0],
    }
    for c in countries
]
```

---

## 7. Complete Production Pattern

```python
import requests, time, random

def fetch_all_pages(base_url, params=None, page_param='_page',
                    limit_param='_limit', page_size=10,
                    delay=0.5, max_retries=3):
    """
    Fetch all pages from a paginated endpoint with throttling and retry.
    Returns flat list of all records.
    """
    params = dict(params or {})
    params[limit_param] = page_size
    all_records, page = [], 1

    while True:
        params[page_param] = page
        data = get_with_retry(base_url, params=params, max_retries=max_retries)

        if not data:
            break

        all_records.extend(data)
        print(f'Page {page}: +{len(data)} records (total: {len(all_records)})')
        page += 1
        time.sleep(delay)

    return all_records
```

---

## 8. Interview Checklist

- [ ] `requests.get(url, params=..., timeout=10)` — always set timeout
- [ ] `resp.raise_for_status()` — surfaces 4xx/5xx immediately
- [ ] Pagination: loop until empty page, or `next` is None
- [ ] Throttling: `time.sleep(delay)` between pages / respect `Retry-After`
- [ ] Retry: exponential backoff on 429 and 5xx; raise immediately on 4xx
- [ ] Jitter: add `random.uniform(0, 0.5)` to backoff — avoids thundering herd
- [ ] `resp.json()` only after confirming status is 200
- [ ] Use `params=` dict in `requests.get()`, NOT f-string URL (handles encoding)

---

## 9. Quick Reference

| Task | Code |
|------|------|
| GET request | `requests.get(url, params={}, timeout=10)` |
| Parse JSON | `resp.json()` |
| Check status | `resp.raise_for_status()` |
| Status code | `resp.status_code` |
| Response header | `resp.headers['Retry-After']` |
| Paginate loop | `while True: ... if not batch: break; page += 1` |
| Fixed throttle | `time.sleep(0.5)` |
| Retry-After header | `int(resp.headers.get('Retry-After', 5))` |
| Exponential backoff | `wait = base_delay * (2 ** attempt)` |
| Jitter | `wait += random.uniform(0, 0.5)` |
