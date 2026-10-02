---
layout: page
title: "How to Estimate Search Volume From Google Trends (Turn 0–100 Into Real Numbers)"
description: "Google Trends shows relative interest on a 0–100 scale, not search counts. With one keyword whose monthly volume you know, you can estimate real search volume for every other keyword. Here is the method, the formula and the pitfalls."
permalink: /google-trends-search-volume/
nav_title: "Search volume"
nav_order: 3
---

Google Trends never tells you how many people searched for something. A value of 100 means "the highest point in this chart" and 50 means "half of that", whether that's 5 million searches or 500. But Trends values are **proportional to search volume**. So if you know the real volume of *one* keyword, you can estimate the volume of every other keyword measured on the same scale.

## Why it works

For each place and point in time, Google Trends divides a keyword's searches by all searches made there and then, and scales the result so the chart's highest point is 100. Every keyword in the same chart goes through the same scaling, so the ratio of two keywords' values equals the ratio of their search volumes:

`volume of B ≈ volume of A × (Trends value of B ÷ Trends value of A)`

This only holds **when A and B are on the same scale**: the same comparison, or several comparisons stitched together through a shared anchor keyword ([how that works](../)). You can't plug values from two separate Google Trends charts into this formula, because each chart has its own 100.

## Step by step

**1. Pick a calibration keyword with a known monthly volume.** Two common sources:

- **Google Ads Keyword Planner**: "Avg. monthly searches" for the last 12 months. Without an active ad campaign it only shows ranges like 10K–100K, which is too coarse to calibrate with. Accounts with ad spend see rounded numbers.
- **SEO tools** (Semrush, Ahrefs and others): their own estimates, usually as single numbers.

Choose a keyword that is **mid-sized compared with your list**, has a steady trend (no viral spikes) and is unambiguous.

**2. Put the calibration keyword and all your other keywords on one Trends scale.** Use the **same location** as your volume source (Keyword Planner "United States" means Trends location US), the **past 12 months** (matching "avg. monthly searches"), **web search** and **all categories**.

**3. Compute a multiplier:**

`multiplier = known monthly volume of the calibration keyword ÷ its average Trends value`

**4. Multiply every other keyword's average Trends value by it:**

`estimated monthly searches = average Trends value × multiplier`

### Worked example

*Illustrative numbers, not real data.* Say Keyword Planner gives "running shoes" 450,000 searches a month in the US, and on a common 12-month Trends scale its average is 60:

`multiplier = 450,000 ÷ 60 = 7,500`

| Keyword | Average Trends value (common scale) | Estimated monthly searches |
|---|---|---|
| running shoes (calibration) | 60 | 450,000 (known) |
| trail running shoes | 12 | 90,000 |
| barefoot shoes | 4.5 | ~34,000 |
| zero drop shoes | 0.8 | ~6,000 |

The timeline converts the same way. If "running shoes" reaches 72 in one week of November, that week's searches were running at about 72 × 7,500 = **540,000 a month**. Read weekly values as "searches per month at that week's pace".

## Pitfalls that make estimates wrong

**1. Rounding on small values.** Google reports whole numbers. If a keyword averages 0.8, Google's rounding alone can shift it by more than half its value, and the estimate with it. Keywords far smaller than the biggest one in their comparison need to be re-measured next to a smaller "bridge" keyword before their value means anything. The same goes for the calibration keyword: it should register clearly, not hover around 1.

**2. Mismatched settings.** The location, period and search type must match your volume source. US volumes don't calibrate a worldwide chart, and a 12-month average doesn't calibrate a 5-year chart.

**3. Keyword Planner groups close variants.** It often reports one volume for "running shoe" and "running shoes", while Trends measures the exact search term you typed. Use the same form on both sides. Better still, calibrate with **two or three keywords** and compare their multipliers: if they disagree a lot, one source is grouping or rounding that keyword differently, so drop it.

**4. Search terms vs topics.** Trends "topics" include related searches in every language, but volume tools measure exact search terms. Calibrate with search terms.

**5. Sampling.** Trends is built from a sample of searches and ignores repeated searches by the same person over a short time, so two requests can differ by a few percent.

Done carefully, the estimates are good for **ranking keywords, sizing a niche and spotting the order of magnitude** of keywords your volume tool doesn't cover. Treat them as estimates, not exact counts.

## Doing it for a long keyword list

With up to 8 keywords you can read the values straight off one Google Trends chart. For more, you need the anchor method to get everything on one scale first, which is manual work for long lists.

I maintain a tool that does the stitching automatically: **[Google Trends Scraper — Unlimited Keywords](https://apify.com/ambitious_vagabond/google-trends-unlimited)** on Apify. Add your calibration keyword to the list. Each result has an `average` on one common scale shared by all keywords, plus a `precision` label that tells you how reliable that keyword's value is. Then:

- **No code:** run it in the browser, download the summary as Excel or CSV, and add a column `= average × multiplier`.
- **Python:** `pip install apify-client` (version 3 or newer), then:

```python
from apify_client import ApifyClient

CALIBRATION = ("running shoes", 450_000)  # keyword, monthly searches from Keyword Planner
keywords = ["trail running shoes", "barefoot shoes", "zero drop shoes", "carbon plate running shoes"]

client = ApifyClient("YOUR_APIFY_TOKEN")
run = client.actor("ambitious_vagabond/google-trends-unlimited").call(run_input={
    "searchTerms": [CALIBRATION[0], *keywords],
    "timeRange": "today 12-m",  # match Keyword Planner's 12-month average
    "geo": "US",                # match Keyword Planner's location
})
items = {i["keyword"]: i for i in client.dataset(run.default_dataset_id).iterate_items()}

multiplier = CALIBRATION[1] / items[CALIBRATION[0]]["average"]
for kw, item in sorted(items.items(), key=lambda kv: -(kv[1]["average"] or 0)):
    if item["average"]:
        print(f'{kw:28} ~{item["average"] * multiplier:>9,.0f} / month   precision: {item["precision"]}')
```

It costs **$2 per 1,000 keywords**, and Apify's free plan includes monthly credits, so small lists are free.

## FAQ

**Does Google Trends show search volume?**
No. It shows relative interest from 0 to 100. You need one keyword with a known volume to turn it into estimated searches, as described above.

**How accurate is this?**
At best as accurate as your calibration number, plus a few percent of Trends sampling noise. Errors grow quickly for keywords that are tiny compared with the others in their chart, unless they were measured next to a bridge keyword.

**Can I use Google Search Console data to calibrate?**
Only roughly. Impressions count how often *your page* was shown for a query, not how often the query was searched, so they undercount unless you rank at the very top.

**Why don't Keyword Planner and Trends agree month by month?**
Keyword Planner rounds and groups variants, and Trends is sampled and scaled to search share. Calibrate on 12-month averages, not on single months.

## More guides

- **[How to compare more than 5 keywords in Google Trends](../)**: the anchor-keyword method, step by step.
- **[Bulk Google Trends check: which of your keywords are rising](../bulk-google-trends/)**: trend direction, year-over-year growth and seasonality for a whole keyword list.
- **[pytrends is archived: how to get Google Trends data in Python in 2026](../pytrends-alternative/)**: what still works after pytrends.
