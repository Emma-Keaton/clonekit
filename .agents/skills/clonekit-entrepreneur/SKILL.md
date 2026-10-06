---
name: clonekit-entrepreneur
description: >-
  Researches the app being cloned and reads what its real users say in public
  reviews (App Store, Google Play, G2, Capterra, Trustpilot, Reddit, Hacker
  News, its own feature-request board), then ranks what they hate, what is
  missing and what is unsolved, turns it into a fix plan for the clone and a
  positioning angle you can sell. Every quote is real, verbatim and linked.
  Use when the user says "what do people hate about X", "read the reviews",
  "how do I make mine better", "find the gap", "what features are missing",
  "how do I position this", "make it sellable", or after /clonekit-diff.
---

# clonekit-entrepreneur

A straight copy of an app has no reason to exist. This skill finds the reason:
what the original's users hate, in their own words, and fixes it in yours.

Tool in this folder:

```bash
./bin/replica reviews clonekit/reviews.csv --out clonekit/feedback.md
```

## Reads and writes

Reads:

Public review sources for the original app (never invented rows)

Writes:

- `clonekit/reviews.csv` (`source,url,date,rating,text`; every row linked)
- `clonekit/feedback.md` (from the tool)
- `clonekit/fixes.md` (three lists, fix plan, angle)
- new rows in `clonekit/features.csv` with `original` set to `no`

Tools: ./bin/replica reviews clonekit/reviews.csv --out clonekit/feedback.md (fallback: `python3 .agents/skills/clonekit-entrepreneur/reviews.py ...`)

## The rules, which are not negotiable

- **Never fabricate.** No invented reviews, quotes, ratings, counts, users or
  sources. If a source cannot be reached, say so and move on. If there are 14
  reviews, say 14.
- **Every quote is verbatim and linked.** Copied exactly from the page, with
  the URL of the review or thread. `reviews.py` drops any row without a link.
- **Reading, not scraping.** Read review pages the way a person does, in the
  browser, and copy rows into the sheet. No scraping libraries against stores
  or review sites whose terms forbid it. Official public feeds and APIs are
  fine within their terms: Apple's customer reviews RSS feed
  (`https://itunes.apple.com/us/rss/customerreviews/id=<APP_ID>/sortBy=mostRecent/json`),
  the Hacker News Algolia API (`hn.algolia.com/api/v1/search?query=...`),
  Reddit's official API under its terms.
- **No fake reviews, ever.** Not for your app, not against theirs. It is
  illegal in the US (the FTC's 2024 rule) and in many other places.
- **Reviewers are not your testimonials.** Their words are research. Do not
  put them on your landing page.

## Step 1: collect

Aim for 100+ reviews across at least three sources, recent first:

| source | where |
| --- | --- |
| App Store | the app page, Ratings and Reviews, See All; or the RSS feed above |
| Google Play | the listing, See all reviews, sort by newest |
| G2, Capterra, Trustpilot | the product's review pages, filter to 1 to 3 stars too |
| Reddit | search "X alternative", "switched from X", "X sucks", "X vs" |
| Hacker News | the Algolia API or site search, same queries |
| the original's own board | its public roadmap or feature-request board (Canny and similar) and the vote counts |
| its changelog | what it shipped, so you do not "fix" what is already fixed |

Each row in `clonekit/reviews.csv`: `source,url,date,rating,text`, text copied
exactly. Read the 3 and 4 star reviews too. "Love it, but..." is where the
best fixes hide.

## Step 2: rank

```bash
./bin/replica reviews clonekit/reviews.csv --out clonekit/feedback.md
```

It sorts reviews into themes (`themes.json`, edit it for the app's category),
weights low ratings and recent reviews higher, marks themes with fewer than 3
reviews or only one source as thin, lists every request in the users' own
words, and surfaces low ratings that matched no theme. Read that last list by
hand. It is often the best part.

## Step 3: three lists

From `feedback.md`, write three ranked lists. Each item: the problem in one
line, how many reviews, how many sources, one or two linked quotes.

1. **What they hate.** Complaints about things the app does.
2. **What is missing.** Features people ask for by name.
3. **What is unsolved.** Whole jobs or groups the app ignores ("not built for
   teams", "useless for therapists"). These become positioning.

Thin themes are listed as thin. Do not present three angry Reddit comments as
a trend.

## Step 4: the fix plan

Pick the top 5 to 8 by evidence times how cheaply you can fix them. For each:
what to build or change, size (S, M, L), which skill does it, and the
evidence. Add each one to `clonekit/features.csv` as a row with `original` set
to `no`. Pricing and billing complaints go to `/clonekit-launch`.

## Step 5: the angle

Three positioning options, each grounded in a top theme:

```
For {{who}} who {{hate this about the original, in plain words}},
{{your app}} {{does this instead}}.
Evidence: {{theme}}, {{n}} reviews across {{n}} sources.
```

Recommend one. It drives clonekit-brand's name and voice and clonekit-launch's
hero. Do not put the original's name in your app name, ads or store listing.
A factual comparison page is a legal question for a lawyer in your country.

## Output

`clonekit/reviews.csv`, `clonekit/feedback.md`, `clonekit/fixes.md` (three
lists, fix plan, angle), new rows in `features.csv`, and a summary that
states the sample size. Next: `/clonekit-brand`.

## Done when

- [ ] 100+ real reviews from 3+ sources collected (or the real, smaller number stated)
- [ ] `./bin/replica reviews` run; thin themes marked; unthemed low ratings read by hand
- [ ] Three ranked lists: hate, missing, unsolved, each with counts and linked quotes
- [ ] Fix plan of 5 to 8 items sized S/M/L, added to `features.csv`
- [ ] Three positioning angles with evidence; one recommended; sample size stated everywhere

## Handoff

Update `clonekit/status.json`: set `clonekit-entrepreneur` to `done` (or `blocked`, with the reason), list the artifacts you wrote, and set `next` to `brand`.
Then name the next skill to the user: **clonekit-brand**.
