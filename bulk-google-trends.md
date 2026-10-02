---
layout: page
title: "Bulk Google Trends Check: Find Which of Your Keywords Are Rising (50–500 Keywords)"
description: "Check Google Trends for a whole keyword list at once: which keywords are growing, falling, seasonal or spiky, all on one comparable scale. A no-code way and a Python script with year-over-year growth."
permalink: /bulk-google-trends/
nav_title: "Bulk trend check"
nav_order: 4
---

You have a keyword list from Keyword Planner, Search Console, a product catalog or a content plan, and you want to know four things about every keyword: **how big is it, is it growing or dying, is it seasonal, and was it a one-off spike?**

On the Google Trends website that means typing keywords into charts 5 at a time (8 in the new Explore), reading each chart by eye, and remembering that every chart has its own 0–100 scale. That's fine for 10 keywords and painful for 100. This guide shows how to check a whole list at once.

## What to measure for each keyword

- **Size:** the keyword's average interest over the period, **on a scale shared by all keywords**. Without a shared scale you can't rank keywords from different charts ([why](../)).
- **Direction:** recent interest compared with earlier interest. Compare the **last 12 months with the 12 months before** (year-over-year). Comparing this quarter with last quarter mostly measures seasonality: "sunscreen" always "rises" in spring.
- **Seasonality:** whether the keyword peaks at the same time every year. Use at least 3 years of data to see it.
- **Spikiness:** the peak divided by the average. A keyword whose peak is 10× its average was driven by news or a viral moment, so check what happened on the peak date before you build anything on it.

## The no-code way

I maintain **[Google Trends Scraper — Unlimited Keywords](https://apify.com/ambitious_vagabond/google-trends-unlimited)** on Apify, which puts any number of keywords on one common scale and summarizes each one:

1. Open the tool and click **Try for free**.
2. Paste your keywords, one per line: 50, 200 or 500.
3. Pick a **location** and set the time range to **Past 5 years** (weekly data, long enough for year-over-year growth and seasonality).
4. Click **Start**, then download the results as **Excel or CSV**.

Each keyword comes back as one row:

| Column | What it tells you |
|---|---|
| `average` | Size, on a 0–100 scale shared by every keyword in the run. Sort by it to rank keywords. |
| `max`, `peakDate` | The highest point and when it happened. `max ÷ average` = spikiness. |
| `latest` | The most recent complete week. |
| `changePercent` | The average of the last quarter of the period vs. the first quarter. With Past 5 years, that's roughly the last 15 months vs. the first 15 months. |
| `trend` | `rising` (above +20 %), `falling` (below −20 %) or `stable`, based on `changePercent`. |
| `precision` | How finely Google's rounded data could measure the keyword: `high`, `medium`, `low` or `too small`. |
| `timeline` | Every data point (date and value) for charts or your own calculations. |

It costs **$2 per 1,000 keywords**, so a 500-keyword list costs about $1. Apify's free plan includes monthly credits, which cover a couple of thousand keywords a month.

## Year-over-year growth with Python

`changePercent` is a quick five-year view. For a precise year-over-year number, compute it from the weekly timeline. `pip install apify-client pandas`, put your keywords in `keywords.txt` (one per line), and run:

```python
import pandas as pd
from apify_client import ApifyClient

keywords = [k.strip() for k in open("keywords.txt", encoding="utf-8") if k.strip()]

client = ApifyClient("YOUR_APIFY_TOKEN")
run = client.actor("ambitious_vagabond/google-trends-unlimited").call(run_input={
    "searchTerms": keywords,
    "timeRange": "today 5-y",  # weekly data points
    "geo": "US",
})

rows = []
for item in client.dataset(run.default_dataset_id).iterate_items():
    weekly = [p["value"] for p in item["timeline"] if not p["isPartial"] and p["value"] is not None]
    if len(weekly) < 104 or not item["average"]:
        continue
    last_year, year_before = sum(weekly[-52:]) / 52, sum(weekly[-104:-52]) / 52
    rows.append({
        "keyword": item["keyword"],
        "size": item["average"],
        "yoy_%": round((last_year / year_before - 1) * 100, 1) if year_before else None,
        "spikiness": round(item["max"] / item["average"], 1),
        "peak": item["peakDate"],
        "precision": item["precision"],
    })

df = pd.DataFrame(rows).sort_values("yoy_%", ascending=False)
print(df.head(20).to_string(index=False))
df.to_csv("keyword_trends.csv", index=False)
```

## Reading the results

- **Big and rising:** the obvious priorities. Expect competition.
- **Small but rising fast:** early opportunities. Keyword tools often show tiny or zero volume for these because their data lags.
- **Falling year over year:** deprioritize, or refresh existing content before it decays further.
- **Spiky (peak far above average):** news-driven. Check `peakDate`; interest may already be gone.
- **Seasonal:** plan publishing a few weeks *before* the yearly peak, not during it.
- **Low precision or "too small":** the keyword barely registers compared with the others. Treat it as "very small", and don't read its growth rate literally.

To turn the shared 0–100 scale into estimated monthly searches, see **[how to estimate search volume from Google Trends](../google-trends-search-volume/)**.

## Doing it by hand

For up to about 20 keywords you can do this on the Google Trends website with the anchor-keyword method: one shared keyword in every chart, then rescale each chart so the anchor matches. **[Step-by-step guide](../)**. Past that, the CSV downloads and the rescaling spreadsheet take longer than the analysis itself.

## FAQ

**How many keywords can I check at once?**
The tool has no keyword limit. Google is still queried a few keywords at a time behind the scenes, so long lists take longer to run.

**Why not just use Keyword Planner's "YoY change" column?**
Use it as a second opinion. Keyword Planner's volumes are rounded and grouped by close variants, and exact numbers need an active ad campaign. Trends gives weekly granularity, history back to 2004, and sub-regions like states and cities.

**Can I check trends by country or state?**
Yes. Set the location to a country (`DE`) or a sub-region (`US-CA`). Every keyword in the run uses the same location, so they stay comparable.

## More guides

- **[How to compare more than 5 keywords in Google Trends](../)**: the anchor-keyword method, step by step.
- **[How to estimate search volume from Google Trends](../google-trends-search-volume/)**: turn 0–100 into estimated monthly searches.
- **[pytrends is archived: how to get Google Trends data in Python in 2026](../pytrends-alternative/)**: what still works after pytrends.
