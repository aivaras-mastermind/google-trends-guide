---
layout: page
title: "Why Does Google Trends Data Change? (Different Results Each Time, Explained)"
description: "Google Trends can give different numbers for the same search on different days. The causes are sampling, whole-number rounding and per-chart scaling. How to get stable numbers."
permalink: /google-trends-data-changes/
nav_title: "Why data changes"
nav_order: 5
---

You download Google Trends data for a keyword, come back a day later with exactly the same settings, and the numbers are different. Or your script (pytrends, an API, a scraper) returns values that don't match what the Google Trends website shows. Nothing is broken. Google Trends is built in a way that makes this normal, and once you know the causes you can get numbers stable enough to rely on.

## The short answer

Google Trends doesn't count every search. It works from a **sample** of searches, and a new sample means slightly different numbers. On top of that, values are **rounded to whole numbers** and **scaled so the highest point in each chart is 100**, so a small change in one place can shift every value in the chart. Small keywords, small regions and short time ranges are hit hardest.

## 1. Sampling: Trends is built from a sample of searches

Google says it directly in its [Trends data FAQ](https://support.google.com/trends/answer/4365533): "only a sample of Google searches are used in Google Trends". The sample is large enough to show the shape of interest in popular terms, but it is still a sample, and different samples give different values.

Researchers who downloaded the same queries many times found how this plays out in practice. [Djorno, Santillana and Yang (2025)](https://arxiv.org/abs/2504.07032) report that repeated requests on the same day return the same cached result, and that a new sample is drawn after the cache resets at **midnight UTC**, which is why numbers change from one day to the next rather than from one click to the next. They also cite earlier work showing that popular keywords stay consistent across samples while rare ones vary much more.

Google also adds noise on purpose. The same FAQ says Trends incorporates "statistical noise that includes small and random fluctuations that don't represent actual search behavior", and that it is "most noticeable on queries with low or no search interest".

## 2. Whole-number rounding

Trends reports whole numbers from 0 to 100. For a big keyword the rounding hardly matters: 63 versus 64 is a difference of under 2 %. For a small one it dominates. A keyword that "really" sits at 1.4 shows as 1, and one at 0.4 shows as 0 (the website shows "<1"). If its true value moves from 1.4 to 1.6 between two samples, the reported value jumps from 1 to 2, which looks like doubling.

Google's FAQ also says that "search terms with low volume appear as '0'". So a keyword can flicker between 0 and a small number across pulls without anything real changing.

## 3. Every chart is scaled to its own 100

Each data point is divided by all searches in that place and time, and then, in Google's words, "the resulting numbers are then scaled on a range of 0 to 100". The 100 is the highest point **in that particular chart**. That has three consequences that often look like "the data changed":

- **Adding or removing a keyword changes the others.** If the new keyword is bigger, it takes the 100 and every other value shrinks.
- **A different time range changes the values.** "Past 12 months" and "past 5 years" have different highest points and different time steps (weeks versus months), so the same week gets a different number in each.
- **A new peak rescales the history.** In a rolling range like "past 90 days", a spike this week becomes the new 100 and pushes every earlier value down.

Location, category and search type (web, YouTube, news, images, Shopping) change the scale in the same way. Two downloads are only comparable when all of these settings match.

## 4. The last data point is incomplete

The most recent week (or day, or hour) is usually still in progress. Google marks it as partial, and its value goes up as the period fills in. If you compare yesterday's download with today's, the last point will almost always differ. Leave partial points out of averages and trend calculations.

## 5. Google changes its data collection

Some charts carry a note that an improvement to Google's data collection system was applied from a certain date. Values before and after such a date aren't strictly comparable. Researchers have documented at least one such change, in January 2022, that raised measured search volumes ([as cited by Djorno et al.](https://arxiv.org/abs/2504.07032)). If your series crosses one of these dates, expect a step that may not reflect real behavior.

## Why your script doesn't match the website

The website and scripts read from the same Trends backend, so the usual reasons for a mismatch are the ones above:

- **A different day**, so a different sample. Pull both on the same UTC day before comparing.
- **Different settings.** Check location, time range, category, search type and the exact list of keywords. One extra keyword changes the scale.
- **Search term versus topic.** The website suggests topics (e.g. "Python (Programming language)") which include related searches in every language. A script that sends plain text measures the exact search term.
- **Rounding of your own.** Normalizing whole numbers again (for example dividing by a max of 37) carries the rounding error into every value.

## How to get stable numbers

**1. Average several samples taken on different days.** This is the standard fix in the research literature: [Eichenauer et al. (2022)](https://ideas.repec.org/a/bla/ecinqu/v60y2022i2p694-705.html) propose drawing many samples and averaging them. Because the sample only changes once a day, the pulls have to be on **different UTC days**. Each pull is scaled to its own 100, so average them and then rescale the result to 0–100.

*Illustrative numbers, not real data.* Three pulls of the same weekly series:

| Week | Pull 1 | Pull 2 | Pull 3 | Average |
|---|---|---|---|---|
| Sep 7 | 41 | 44 | 40 | 41.7 |
| Sep 14 | 100 | 97 | 100 | 99.0 |
| Sep 21 | 63 | 66 | 61 | 63.3 |

With pandas, if each pull is a DataFrame indexed by date with one column per keyword:

```python
import pandas as pd

def average_pulls(pulls: list[pd.DataFrame]) -> pd.DataFrame:
    """Average Google Trends pulls taken on different days, then rescale to 0-100."""
    avg = pd.concat(pulls).groupby(level=0).mean()
    return avg / avg.max().max() * 100
```

**2. Compare averages, not single points.** An average over a whole year moves much less between samples than one week does. Rank keywords by their averages.

**3. Use longer time ranges and bigger regions where you can.** More searches per data point means less sampling noise. A worldwide 5-year chart is far steadier than a city-level 7-day chart.

**4. Don't let small keywords sit next to a giant.** Next to a keyword that peaks at 100, anything that averages under 1 is mostly rounding. Compare small keywords with others of similar size, or step down through a chain of medium-sized "bridge" keywords ([the anchor method](../) explains how).

**5. Drop the partial last point** and keep every setting identical between pulls.

**6. Record when you pulled the data.** Store the download date with every dataset so you can tell real changes from sample changes later.

## Automating repeated pulls

Averaging several days by hand gets tedious for more than a few keywords. I maintain **[Google Trends Scraper — Unlimited Keywords](https://apify.com/ambitious_vagabond/google-trends-unlimited)** on Apify, which helps with two of the problems above: it puts any number of keywords on one common scale, re-measures small keywords next to smaller bridge keywords so they don't round to 0, and labels each keyword's `precision`. Every timeline point carries `isPartial`, so you can drop the incomplete period. Run it with an Apify schedule once a day for a few days and average the `timeline` values of each run with the function above. It costs $2 per 1,000 keywords, and Apify's free plan includes monthly credits.

## FAQ

**Why does Google Trends show different results each time?**
Because it is based on a sample of searches, and the sample changes from day to day. Rounding to whole numbers and scaling each chart to its own 100 make small differences look bigger, especially for low-volume keywords.

**Will I get the same numbers if I search twice on the same day?**
Usually yes. Researchers found that results are cached and a new sample is drawn after midnight UTC, so same-day pulls tend to match and next-day pulls differ.

**How many samples should I average?**
Research doesn't agree on one number, and it depends on how small your keywords are. A handful of pulls on different days removes most of the noise for mid-sized keywords. Rare keywords may need more.

**Why did a keyword's value drop to 0?**
Either it really had too little search interest in that period, or it fell below Google's threshold in that sample. Google shows low-volume terms as 0. Check whether a bigger keyword in the same chart is pushing it down.

**Is Google Trends data reliable?**
For the shape of interest in popular keywords, yes. For tiny keywords, single weeks or small regions, treat each pull as one noisy measurement and average several.

## More guides

- **[How to compare more than 5 keywords in Google Trends](../)**: the anchor-keyword method, which also fixes the rounding problem for small keywords.
- **[How to estimate search volume from Google Trends](../google-trends-search-volume/)**: turn the 0–100 scale into estimated monthly searches.
- **[pytrends is archived: how to get Google Trends data in Python in 2026](../pytrends-alternative/)**: what still works after pytrends.
