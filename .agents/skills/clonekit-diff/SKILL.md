---
name: clonekit-diff
description: >-
  Compares an app clone against the original: a feature parity score from the
  feature matrix (weighted by must, should, could) with the missing list in
  build order, plus a screenshot layout diff that ignores colour so a rebrand
  does not count against you. Two standard-library Python tools. Use when the
  user says "how close is my clone", "compare it to the original", "what's
  missing", "parity check", "diff the screens", "is it ready", or after
  /clonekit-test.
---

# clonekit-diff

Two tools in this folder, both standard-library Python, no installs:

```bash
./bin/replica parity clonekit/features.csv                         # feature parity + missing list
./bin/replica imgdiff clonekit/screens/S07.png clonekit/clone-screens/S07.png --out diff-S07.png
./bin/replica imgdiff a.png b.png --json > clonekit/diffs/S07.json # for parity.py --visual
./bin/replica parity clonekit/features.csv --visual clonekit/diffs/*.json --markdown > clonekit/parity.md
```

## Reads and writes

Reads:

- `clonekit/features.csv`
- `clonekit/screens/` and `clonekit/clone-screens/` screenshots

Writes:

- `clonekit/parity.md` (scores, missing list, behaviour diff, verdict)
- `clonekit/diffs/` layout diff images and JSON

Tools: ./bin/replica parity clonekit/features.csv and ./bin/replica imgdiff <original.png> <clone.png> (fallbacks: `python3 .agents/skills/clonekit-diff/parity.py ...`, `python3 .agents/skills/clonekit-diff/imgdiff.py ...`)

## What parity means here

**Parity means it does the same job, not that it looks the same.** The
feature score is the number that matters: can a user do everything they could
do in the original. The layout score checks structure (is the information in
the same places, in the same hierarchy), because that is what makes a switcher
feel at home. It deliberately ignores colour, because clonekit-brand changes
every colour on purpose. Do not chase pixel parity with the original. Its
exact look is its trade dress, and it changes before launch.

## Step 1: feature parity

Make sure `clonekit/features.csv` is current: every row's `clone` column is
`yes`, `partial` (with a note), `no`, or `skip` (with a reason). Then:

```bash
./bin/replica parity clonekit/features.csv
```

It weights must 3, should 2, could 1, counts partial as half, leaves out
`skip` rows and rows you added that the original does not have, and prints:
the score, must-haves done of total, each area weakest first, and the missing
list in build order. Must-haves not done means not shippable, and it says so.

## Step 2: layout diff

For each key screen, take two screenshots at the **same viewport** (1440x900
desktop, 390x844 mobile) in the **same state** (same data shape, same tab
open, logged in the same way). The original's come from public pages or the
user's own account, saved in `clonekit/screens/`. The clone's go in
`clonekit/clone-screens/`.

```bash
./bin/replica imgdiff clonekit/screens/S07.png clonekit/clone-screens/S07.png --out clonekit/diffs/S07.png
```

Layout mode (default) turns both into edge maps, cuts them into a grid, and
compares where things are, scoring only cells with something in them. It
reports the score (matches 90+, close 75+, partly 50+, different), the
regions that differ (in the original's pixel coordinates, biggest first), and
a height difference if the clone's page is much longer or shorter. Retina and
non-retina screenshots compare fine: both are scaled to the same width.

`--mode pixel` is exact comparison. Use it for your own regressions (clone
today against clone last week), not against the original.

## Step 3: behaviour diff

Walk each flow in both apps and compare what the scores cannot see: clicks to
finish the core flow, what happens on errors, what is remembered between
visits, what emails arrive. Fewer clicks than the original is a win. Write
each difference as: flow, original does, clone does, fix or keep.

## Step 4: the report

`clonekit/parity.md`: overall score, feature score, layout score per screen,
missing features in build order, behaviour differences, and a verdict:

- **not shippable**: any must-have missing, or any open S1 bug
- **shippable**: all must-haves done, feature score 80+, no open S1 or S2
- **better than the original**: shippable, plus fixes from
  clonekit-entrepreneur. This is the goal. A straight copy has no reason to exist.

Give honest numbers. A clone at 62% is at 62%.

## Output

`clonekit/parity.md`, the diff images, and the top five things to build next.
Then `/clonekit-build` for the gaps, or `/clonekit-entrepreneur` if parity is
there.

## Done when

- [ ] Feature score computed; skip rows and extras excluded; problems in the matrix reported
- [ ] Layout diffs run at matched viewports for each key screen
- [ ] Behaviour diff written: flow, original does, clone does, fix or keep
- [ ] Verdict stated honestly: not shippable / shippable / better than the original
- [ ] Top five things to build next named

## Handoff

Update `clonekit/status.json`: set `clonekit-diff` to `done` (or `blocked`, with the reason), list the artifacts you wrote, and set `next` to `entrepreneur`. If must-haves are missing, set `next` to `build` instead and stop there.
Then name the next skill to the user: **clonekit-entrepreneur**.
