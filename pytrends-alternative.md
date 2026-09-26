---
layout: page
title: "pytrends Is Archived: How to Get Google Trends Data in Python in 2026"
description: "pytrends is archived and keeps failing with 429 errors. Here are the ways to get Google Trends data in Python that still work in 2026 — the official alpha API, a do-it-yourself client, and a managed API — with code."
permalink: /pytrends-alternative/
---

For years, **pytrends** was the default way to pull Google Trends data into Python. Today its GitHub repository is **archived (read-only)**: no new releases, no fixes, and well over a hundred open issues — dozens of them about the same error:

```
pytrends.exceptions.TooManyRequestsError: The request failed: Google returned a response with code 429
```

If your scripts or notebooks broke, this guide covers what still works in 2026, with code for each option.

## Why pytrends fails with 429 errors

Google Trends has never had a public, general-purpose API. pytrends worked by calling the same internal endpoints the Google Trends website uses. Google **rate-limits** those endpoints per IP address — and much more aggressively for IPs of cloud providers (AWS, GCP, Colab, CI runners). A few dozen quick requests are often enough to get `429 Too Many Requests` for minutes or hours. With the library unmaintained, nobody is adapting it when Google tightens limits or changes response formats.

## Option 1: The official Google Trends API (alpha)

Google announced an [official Google Trends API](https://developers.google.com/search/blog/2025/07/trends-api) in July 2025. It returns **consistently scaled data** (so numbers from different requests are comparable), up to 5 years back, with daily, weekly, monthly and yearly aggregation and region filters.

The catch: **it is still an application-only alpha.** You apply, join a queue and wait; there is no self-serve key, no published pricing and no date for general availability. Apply if you have a long-term project — but you probably can't build on it today.

## Option 2: Your own minimal client

You can call the same endpoints pytrends used. Two requests give you a timeline: `explore` returns widget tokens, and `widgetdata/multiline` returns the data. Using [curl_cffi](https://github.com/lexiforest/curl_cffi) (it looks like a real Chrome browser to Google) instead of `requests` helps:

```python
import json
from curl_cffi import requests

s = requests.Session(impersonate="chrome")
s.get("https://trends.google.com/trends/?geo=US")  # sets the cookie the API expects

req = {"comparisonItem": [{"keyword": k, "geo": "US", "time": "today 12-m"} for k in ["python", "javascript"]],
       "category": 0, "property": ""}
r = s.get("https://trends.google.com/trends/api/explore",
          params={"hl": "en-US", "tz": "0", "req": json.dumps(req)})
widgets = json.loads(r.text[r.text.index("{"):])["widgets"]      # responses start with )]}' — skip it
ts = next(w for w in widgets if w["id"] == "TIMESERIES")

r = s.get("https://trends.google.com/trends/api/widgetdata/multiline",
          params={"hl": "en-US", "tz": "0", "req": json.dumps(ts["request"]), "token": ts["token"]})
points = json.loads(r.text[r.text.index("{"):])["default"]["timelineData"]
for p in points[:3]:
    print(p["formattedTime"], p["value"])
```

This is fine for occasional use. For anything regular you'll need what pytrends lacked:

- **Retries with backoff and rotating IPs** — from a single IP you *will* hit 429 again.
- **More than 5 keywords** — Google compares at most 5 per request, and every request is scaled so its own maximum is 100. Numbers from different requests aren't comparable until you rescale them through a shared keyword ([how that works](../)).
- **Maintenance** when Google changes these internal endpoints.

## Option 3: A managed Google Trends API (works today)

If you'd rather not run proxies and rescaling yourself, I maintain **[Google Trends Scraper — Unlimited Keywords](https://apify.com/ambitious_vagabond/google-trends-unlimited)** on Apify. You call it like any API:

- **no 429 handling on your side** — sessions and proxies rotate automatically,
- **any number of keywords on one common 0–100 scale** (not just 5 per request), with a precision label per keyword,
- interest over time, **interest by region**, **related queries**, and **trending-now searches** per country,
- **$2 per 1,000 keywords**; Apify's free plan includes monthly credits, enough for a couple of thousand keywords a month.

`pip install apify-client pandas`, then:

```python
import pandas as pd
from apify_client import ApifyClient

client = ApifyClient("YOUR_APIFY_TOKEN")
run = client.actor("ambitious_vagabond/google-trends-unlimited").call(run_input={
    "searchTerms": ["python", "javascript", "typescript", "rust", "go", "kotlin"],
    "timeRange": "today 12-m",
    "geo": "US",
})
items = list(client.dataset(run.default_dataset_id).iterate_items())

# same shape as pytrends' interest_over_time(): dates as rows, one column per keyword
df = pd.DataFrame({i["keyword"]: {p["date"]: p["value"] for p in i["timeline"]} for i in items})
df.index = pd.to_datetime(df.index)
print(df.tail())
```

Each item also has a summary — `average`, `max`, `peakDate`, `latest`, `changePercent`, `trend` — and the timeline marks the current, unfinished period with `isPartial`.

### Migrating from pytrends

| pytrends | Managed API input / output |
|---|---|
| `build_payload(kw_list=[...])` (max 5) | `searchTerms` — any number, one common scale |
| `timeframe="today 12-m"` | `timeRange` — same codes (`now 7-d`, `today 5-y`, `all`…) or `customTimeRange: "2024-01-01 2024-12-31"` |
| `geo="US"` | `geo: "US"` (or a sub-region like `US-CA`) |
| `cat=...` | `category` |
| `gprop="youtube"` | `searchProperty: "youtube"` (also `images`, `news`, `froogle`) |
| `interest_over_time()` | `timeline` on each item (+ summary fields) |
| `interest_by_region(resolution="REGION")` | `includeRegions: true`, `regionResolution: "REGION"` |
| `related_queries()` | `includeRelatedQueries: true` |
| `trending_searches(...)` | `trendingNowCountries: ["US"]` |
| `related_topics()` | not available — Google currently returns empty data for related topics |

## FAQ

**Can I still pip install pytrends?**
Yes, the package still installs and may work for a handful of requests from a home connection. It is unmaintained, though, and 429 errors are very common from cloud servers and notebooks.

**Is there an official Google Trends API?**
Only as an application-based alpha (since July 2025). If you're accepted, it's the most "official" option; otherwise use a client like Option 2 or a managed API like Option 3.

**Why are my numbers different from the Google Trends website?**
Google samples searches and rounds to whole numbers, so two requests can differ by a few percent. Compare keywords within one consistent dataset rather than across separate downloads.

**Is it legal to collect Google Trends data?**
Google Trends shows aggregated, anonymous search-interest statistics — no personal data. You're responsible for how you use the data and for following Google's terms.

---

Related guide: **[How to compare more than 5 keywords in Google Trends](../)** — the anchor-keyword method explained step by step.
