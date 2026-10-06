#!/usr/bin/env python3
"""Post-process extracted skills: add the clonekit contract sections, switch
tool commands to the bin/replica wrapper, remove agent-specific voice, and
rename the --include-replica flag to --include-clonekit."""
import os
import re

ROOT = ".agents/skills"

TOOL_CMDS = [
    ("python3 ../clonekit-design/contrast.py", "./bin/replica contrast"),
    ("python3 ../clonekit-diff/parity.py", "./bin/replica parity"),
    ("python3 ../clonekit-brand/sweep.py", "./bin/replica sweep"),
    ("python3 ../clonekit-launch/listing.py", "./bin/replica listing"),
    ("python3 contrast.py", "./bin/replica contrast"),
    ("python3 sweep.py", "./bin/replica sweep"),
    ("python3 parity.py", "./bin/replica parity"),
    ("python3 imgdiff.py", "./bin/replica imgdiff"),
    ("python3 reviews.py", "./bin/replica reviews"),
    ("python3 listing.py", "./bin/replica listing"),
]

VOICE = [
    ("Claude never signs up for services,", "You never sign up for services,"),
    ("Claude writes `.env.example`", "You write `.env.example`"),
    ("Claude never buys a domain, enters a card,\n  types a password or pastes a live key. Claude writes the exact DNS records,",
     "You never buy a domain, enter a card, type a\n  password or paste a live key. You write the exact DNS records,"),
]

CONTRACT = {
    "clonekit-recon": dict(
        reads="Nothing: this is where a project starts. Bring the app's URL, "
              "its public pages, and (optionally) the user's own account.",
        writes="- `clonekit/recon.md` (template: `recon-map.md` in this folder)\n"
               "- `clonekit/features.csv` (template: `features.csv` in this folder)\n"
               "- `clonekit/screens/` reference screenshots, for layout comparison only",
        tools=None,
        done=[
            "Scope agreed: which app, which platform, which slice, for whom",
            "Sources table with a URL on every row",
            "Screens (S-IDs) with states, flows (F-IDs) with happy-path click counts, components listed",
            "Inferred data model with evidence and a confidence per entity",
            "`clonekit/features.csv` complete; out-of-scope rows are `skip` with a reason",
            "Size estimate (S/M/L/XL) and the five-line summary shown to the user",
        ],
        next_stage="architect",
        note="",
    ),
    "clonekit-architect": dict(
        reads="- `clonekit/recon.md`\n- `clonekit/features.csv`",
        writes="- `clonekit/architecture.md` (template: `architecture.md` in this folder)\n"
               "- `clonekit/schema.sql` (or the first migration)",
        tools=None,
        done=[
            "Stack table: every choice with one line of why; one database, no microservices",
            "Schema: ids, timestamps in UTC, owner columns, decided `on delete` rules, indexes, constraints for the hard races",
            "Access rules chosen and written (RLS or per-query authorisation)",
            "API table: one row per route, plus webhooks and background jobs",
            "The parts that bite, covered: time zones, idempotency, races, rate limits",
            "Build order with milestones naming their screens, tables and routes",
        ],
        next_stage="design",
        note="",
    ),
    "clonekit-design": dict(
        reads="- `clonekit/recon.md`\n- `clonekit/screens/` reference screenshots",
        writes="- `clonekit/design/tokens.json` (template: `tokens.json` in this folder)\n"
               "- `clonekit/design/tokens.css`, the Tailwind theme mapping, `clonekit/design/components.md`\n"
               "- primitives built in isolation (a `/design` route or similar)",
        tools="./bin/replica contrast clonekit/design/tokens.json "
              "(fallback: `python3 .agents/skills/clonekit-design/contrast.py clonekit/design/tokens.json`)",
        done=[
            "Colour roles, type scale, spacing, radius, shadow, motion measured into tokens (role names kept)",
            "`components.md`: every recon component with variants, states, tokens, a11y and the screens it appears on",
            "Primitives built in code from an accessible base, screenshot taken",
            "Zero AA failures: `./bin/replica contrast clonekit/design/tokens.json` exits 0",
            "No raw hex or pixel values in components; no target assets, fonts or copy",
        ],
        next_stage="build",
        note="",
    ),
    "clonekit-build": dict(
        reads="- `clonekit/recon.md`, `clonekit/architecture.md`, `clonekit/design/`\n- `clonekit/features.csv`",
        writes="- the app code, screen by screen\n"
               "- `clonekit/build-log.md`\n"
               "- `clonekit/clone-screens/Sxx.png` screenshots for diffing\n"
               "- the `clone` column of `clonekit/features.csv`",
        tools=None,
        done=[
            "Shell: routing for every screen, layout, tokens wired, primitives, seed data",
            "Vertical slice of the core loop works end to end",
            "Per screen: every recon state plus empty, error, loading; 390px and 1440px; keyboard-reachable; no console errors",
            "No hard-coded copy borrowed from the original; tokens only",
            "`features.csv` rows updated; screenshots saved; build log current",
        ],
        next_stage="backend",
        note=" If the data layer is already real, set `next` to `test` instead.",
    ),
    "clonekit-backend": dict(
        reads="- `clonekit/architecture.md`\n- `clonekit/features.csv`",
        writes="- migrations and server code\n"
               "- `.env.example` (names only, no values)\n"
               "- `clonekit/backend.md` (security checklist, kept ticked)",
        tools=None,
        done=[
            "Sign up, verification, reset, sessions; roles if the recon has them",
            "Access rules on every table, tested with a second user who gets nothing",
            "Payments in test mode: Checkout, Portal, signature-verified idempotent webhooks",
            "Email and jobs wired; integrations use official APIs with the user's own keys",
            "Security checklist fully ticked in `clonekit/backend.md`; feature rows updated",
        ],
        next_stage="test",
        note="",
    ),
    "clonekit-test": dict(
        reads="- `clonekit/recon.md` (the flows)\n- the running app in the project",
        writes="- `clonekit/test-plan.md` (template: `test-plan.md` in this folder)\n"
               "- end-to-end specs in the project's `e2e/` folder (example: `e2e.example.spec.ts`)\n"
               "- `clonekit/bugs.md` (format: `bug-report.md` in this folder)",
        tools=None,
        done=[
            "A numbered case per flow: happy, edge (from the list), negative",
            "Automated specs green: roles-and-labels selectors, console errors, 5xx and axe all failing builds",
            "Manual pass done for what cannot be automated",
            "Every bug reproduced and logged with steps, expected, actual, evidence",
            "No open S1 or S2 bugs (S3/S4 listed and acknowledged)",
        ],
        next_stage="diff",
        note="",
    ),
    "clonekit-diff": dict(
        reads="- `clonekit/features.csv`\n- `clonekit/screens/` and `clonekit/clone-screens/` screenshots",
        writes="- `clonekit/parity.md` (scores, missing list, behaviour diff, verdict)\n"
               "- `clonekit/diffs/` layout diff images and JSON",
        tools="./bin/replica parity clonekit/features.csv and "
              "./bin/replica imgdiff <original.png> <clone.png> "
              "(fallbacks: `python3 .agents/skills/clonekit-diff/parity.py ...`, `python3 .agents/skills/clonekit-diff/imgdiff.py ...`)",
        done=[
            "Feature score computed; skip rows and extras excluded; problems in the matrix reported",
            "Layout diffs run at matched viewports for each key screen",
            "Behaviour diff written: flow, original does, clone does, fix or keep",
            "Verdict stated honestly: not shippable / shippable / better than the original",
            "Top five things to build next named",
        ],
        next_stage="entrepreneur",
        note=" If must-haves are missing, set `next` to `build` instead and stop there.",
    ),
    "clonekit-entrepreneur": dict(
        reads="Public review sources for the original app (never invented rows)",
        writes="- `clonekit/reviews.csv` (`source,url,date,rating,text`; every row linked)\n"
               "- `clonekit/feedback.md` (from the tool)\n"
               "- `clonekit/fixes.md` (three lists, fix plan, angle)\n"
               "- new rows in `clonekit/features.csv` with `original` set to `no`",
        tools="./bin/replica reviews clonekit/reviews.csv --out clonekit/feedback.md "
              "(fallback: `python3 .agents/skills/clonekit-entrepreneur/reviews.py ...`)",
        done=[
            "100+ real reviews from 3+ sources collected (or the real, smaller number stated)",
            "`./bin/replica reviews` run; thin themes marked; unthemed low ratings read by hand",
            "Three ranked lists: hate, missing, unsolved, each with counts and linked quotes",
            "Fix plan of 5 to 8 items sized S/M/L, added to `features.csv`",
            "Three positioning angles with evidence; one recommended; sample size stated everywhere",
        ],
        next_stage="brand",
        note="",
    ),
    "clonekit-brand": dict(
        reads="- `clonekit/fixes.md` (the angle)\n- `clonekit/design/tokens.json` and the codebase",
        writes="- `clonekit/brand.md` (name with checks, palette, logo brief, voice)\n"
               "- `clonekit/brand.json` (`avoid`, `domains`, `colors`)\n"
               "- updated tokens and rewritten strings",
        tools="./bin/replica sweep . --config clonekit/brand.json and "
              "./bin/replica contrast clonekit/design/tokens.json "
              "(fallbacks: `python3 .agents/skills/clonekit-brand/sweep.py ...`, "
              "`python3 .agents/skills/clonekit-design/contrast.py ...`)",
        done=[
            "20 candidates generated, 5 shortlisted, every check marked `to run` or result plus date",
            "New palette in the same token roles, different hue family; contrast exits 0",
            "Logo brief and voice written; 10 key strings rewritten in the new voice",
            "`./bin/replica sweep . --config clonekit/brand.json` exits 0 (clean)",
            "Eyeball check done: favicon, titles, email templates, OG image, app icon",
        ],
        next_stage="launch",
        note="",
    ),
    "clonekit-launch": dict(
        reads="- `clonekit/fixes.md` (the angle and evidence)\n- `clonekit/brand.md`, `clonekit/brand.json`, `clonekit/feedback.md`",
        writes="- `clonekit/launch/landing.md`, `pricing.md`, `listing.json`, `launch-plan.md`\n"
               "- the landing page built in the project",
        tools="./bin/replica listing clonekit/launch/listing.json "
              "(fallback: `python3 .agents/skills/clonekit-launch/listing.py clonekit/launch/listing.json`)",
        done=[
            "Landing page sections written from the angle, then built; contrast check run on it",
            "Pricing table with sources and read dates; billing complaints fixed in the product",
            "`listing.json` filled (start from `listing.example.json`); `./bin/replica listing` exits 0",
            "No invented proof, no reviewer quotes as testimonials, original's name absent",
            "Launch plan: waitlist/beta, communities, first post, first 10 users",
        ],
        next_stage="deploy",
        note="",
    ),
    "clonekit-deploy": dict(
        reads="Everything in `clonekit/`, the test suite, and the tool outputs",
        writes="- `clonekit/deploy.md` (the filled preflight: template `preflight.md` in this folder)",
        tools="./bin/replica parity, ./bin/replica sweep and ./bin/replica listing for the preflight gates",
        done=[
            "Preflight all green: tests, no S1/S2, must-haves done, sweep clean, listing clean, production build",
            "Legal pages live with every processor listed; account deletion works",
            "Production database, env vars, Stripe live, OAuth redirects, verified sending domain",
            "DNS and HTTPS checked; monitoring and alerts on",
            "Core flow done on the live site, and the user has done it on their phone",
        ],
        next_stage=None,
        note="",
    ),
}


def handoff(stage, data):
    ns = data["next_stage"]
    if ns is None:
        return (
            "## Handoff\n\n"
            "Update `clonekit/status.json`: set `deploy` to `done`, list "
            "`clonekit/deploy.md` and the live URL, and clear `next`. The "
            "pipeline is finished: tell the user the app is live under their "
            "own name, and what to watch in the first week.\n"
        )
    return (
        "## Handoff\n\n"
        "Update `clonekit/status.json`: set `%s` to `done` (or `blocked`, with "
        "the reason), list the artifacts you wrote, and set `next` to `%s`.%s\n"
        "Then name the next skill to the user: **clonekit-%s**.\n"
        % (stage, ns, data["note"], ns)
    )


def process(stage):
    path = os.path.join(ROOT, stage, "SKILL.md")
    text = open(path, encoding="utf-8").read()

    for old, new in VOICE:
        text = text.replace(old, new)
    for old, new in TOOL_CMDS:
        text = text.replace(old, new)
    text = re.sub(
        r"\n\(Paths are relative to wherever the pack is installed\..*?on\.\)",
        "\n(Run `./bin/replica <command>` from the project root; the wrapper "
        "finds the tools wherever the pack is installed.)",
        text,
        flags=re.S,
    )

    data = CONTRACT[stage]
    section = "\n## Reads and writes\n\nReads:\n\n%s\n\nWrites:\n\n%s" % (
        data["reads"], data["writes"])
    if data["tools"]:
        section += "\n\nTools: %s" % data["tools"]
    section += "\n"
    m = re.search(r"\n## ", text)
    if not m:
        raise SystemExit("%s: no first heading" % path)
    text = text[: m.start()] + section + text[m.start():]

    done = "\n## Done when\n\n" + "\n".join(
        "- [ ] %s" % item for item in data["done"])
    text = text.rstrip("\n") + "\n" + done + "\n\n" + handoff(stage, data)

    open(path, "w", encoding="utf-8", newline="\n").write(text)
    print("contract added: %s (%d lines)" % (path, len(text.splitlines())))


for stage in CONTRACT:
    process(stage)

# rename the sweep flag everywhere it appears
for rel in ("clonekit-brand/sweep.py", ):
    p = os.path.join(ROOT, rel)
    t = open(p, encoding="utf-8").read()
    t = t.replace("--include-replica", "--include-clonekit")
    t = t.replace("include_replica", "include_clonekit")
    open(p, "w", encoding="utf-8", newline="\n").write(t)
p = "tests/test_sweep.py"
t = open(p, encoding="utf-8").read()
t = t.replace("--include-replica", "--include-clonekit")
t = t.replace("include_replica", "include_clonekit")
t = t.replace("test_include_replica", "test_include_clonekit")
open(p, "w", encoding="utf-8", newline="\n").write(t)
print("renamed include_replica -> include_clonekit")
