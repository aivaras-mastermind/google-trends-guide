---
layout: page
title: "How to Compare More Than 5 Keywords in Google Trends (Free Method + Automated Tool)"
description: "Google Trends only compares 5 keywords at a time, and each comparison has its own 0–100 scale. Here is the anchor-keyword method to compare 10, 50 or 500 keywords correctly — by hand or automatically."
---

Google Trends is the best free source of relative search interest, but it has one frustrating limit: **you can compare at most 5 keywords at once.** Worse, every comparison is scaled on its own: Google sets the highest point *within that comparison* to 100 and scales everything else relative to it. So "40" in one comparison and "40" in another are not the same thing, and you can't simply put two comparisons side by side.

This guide shows how to compare **any number of keywords on one common scale** — first by hand with the *anchor keyword* method, then [automatically with a free-to-try tool](https://apify.com/ambitious_vagabond/google-trends-unlimited).

## Why you can't just combine two Google Trends comparisons

Say you compare `chatgpt, gemini, claude, perplexity, deepseek`, then separately `copilot, grok, llama, mistral, cursor`. In the first comparison ChatGPT is the biggest term, so its peak becomes 100. In the second, Copilot might be the biggest, so *its* peak becomes 100 — even though Copilot has far less search interest than ChatGPT. The two sets of numbers use different units, and averaging or ranking them together gives nonsense.

## The anchor keyword method (free, manual)

The fix is to include **one shared keyword — the anchor — in every comparison**, and use it to convert each comparison onto the same scale.

**Step 1 — Pick a strong anchor.** Use your most-searched keyword. If the anchor is weak, a bigger keyword in the same comparison takes the 100 and the anchor's own numbers become tiny and imprecise.

**Step 2 — Build comparisons of the anchor + 4 other keywords.** Keep **location, time range, category and search type identical** in every comparison.

**Step 3 — Download each comparison** (the ↓ icon on the "Interest over time" chart gives a CSV).

**Step 4 — Compute a scale factor for each comparison.** Take the anchor's **average over the whole period** in your first (reference) comparison and divide it by the anchor's average in the comparison you're converting:

`scale factor = anchor average in reference comparison ÷ anchor average in this comparison`

Multiply every keyword in that comparison by its factor. Use averages (or totals) over all periods, not a single week — one data point is too noisy.

**Step 5 — Rescale to 0–100 (optional).** After converting, the largest single value across all keywords may be above 100. Divide everything by that maximum and multiply by 100 to get a clean common scale.

### Worked example

| Comparison | Anchor (A) average | Other keywords (averages) |
|---|---|---|
| 1 (reference) | A = 80 | B = 40, C = 10, D = 5 |
| 2 | A = 50 | E = 70, F = 20, G = 8 |

In comparison 2, keyword E is bigger than the anchor, so Google gave E the 100 and the anchor only shows 50. The scale factor for comparison 2 is **80 ÷ 50 = 1.6**, so on comparison 1's scale: E = 112, F = 32, G = 12.8. Now every keyword — A to G — is directly comparable.

## The three pitfalls that ruin manual comparisons

**1. Google rounds everything to whole numbers.** A keyword that is 200× smaller than the biggest term in its comparison shows up as `<1` (i.e. 0) almost everywhere. Its "average" is meaningless. The fix is a **bridge keyword**: compare the tiny keywords next to a mid-sized keyword whose value you already know on the common scale, and convert through it. For very long tails you may need several bridges, stepping down in size.

**2. One spike can flatten everything.** If a keyword had a single viral day, that day becomes 100 and the rest of that comparison is squeezed toward zero. Don't use spiky keywords as anchors or bridges.

**3. Results vary slightly between requests.** Google Trends is based on a sample of searches, so the same comparison can come back a few percent different on another day. Do all comparisons in one session, and expect small differences versus the website.

Done carefully, this works — but with 30 keywords it's already 8+ comparisons, CSV downloads and a spreadsheet of factors, and the rounding problem means you also need bridge comparisons for the small terms.

## The automated way

I built a tool that does exactly this — anchor selection, conversion and bridge re-measuring — automatically:
**[Google Trends Scraper — Unlimited Keywords](https://apify.com/ambitious_vagabond/google-trends-unlimited)** on Apify.

You paste in any number of keywords (10, 50, 500) and get:

- the **full interest-over-time timeline for every keyword on one common 0–100 scale**,
- a summary per keyword — **average, peak, latest value, change and trend** (rising / stable / falling),
- a **precision label** per keyword that tells you how finely Google's rounded data could measure it,
- optionally **interest by region**, **related queries**, and **what's trending now** in any country.

In testing, its combined scale matched Google's own side-by-side comparisons **within about 1–3 %** — the size of Google's own rounding — and a keyword 60,000× smaller than YouTube still got a real value instead of `<1`.

It runs in the browser (no code), and results download as **CSV, Excel or JSON**. It costs **$2 per 1,000 keywords**, and Apify's free plan includes monthly credits, so small projects are free.

### Using it from Python

`pip install apify-client` (version 3 or newer), then:

```python
from apify_client import ApifyClient

client = ApifyClient("YOUR_APIFY_TOKEN")
run = client.actor("ambitious_vagabond/google-trends-unlimited").call(run_input={
    "searchTerms": ["python", "javascript", "typescript", "rust", "go", "kotlin", "swift", "java"],
    "timeRange": "today 5-y",
    "geo": "US",
})
for item in client.dataset(run.default_dataset_id).iterate_items():
    print(f'{item["keyword"]:12} avg {item["average"]:>7}  trend {item["trend"]}  precision {item["precision"]}')
```

Each item also contains a `timeline` array (date + value) ready for charts or pandas.

## FAQ

**Can I compare more than 5 keywords directly on the Google Trends website?**
No — the website and its downloads are limited to 5 terms per comparison. You need the anchor method or a tool that applies it.

**Why don't my numbers match the Google Trends website exactly?**
Google samples searches and rounds to whole numbers, so any two requests can differ by a few percent. Relative differences between keywords are what matter.

**What's the best anchor keyword?**
The most-searched keyword in your list, with a smooth (not spiky) trend, in the same location and time range as everything else.

**How small can a keyword be and still be measured?**
Next to one big keyword, anything below about 0.5 % of it rounds to zero. With bridge keywords stepping down in size, much smaller keywords can be measured — the automated tool does this and labels how precise each result is.
