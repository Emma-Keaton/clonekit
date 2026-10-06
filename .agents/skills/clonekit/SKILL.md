---
name: clonekit
description: >-
  The clonekit orchestrator, the entry point for every clone or rebuild
  request. Reads clonekit/status.json to see which of the eleven stages are
  done, routes the user's request to the right skill (including mid-pipeline
  jumps such as "add payments", "name my app" or "how close is my clone"),
  bootstraps new projects with the recon stage, and keeps the state file
  current so any agent can resume in any session. Use when the user says
  "clone this app", "rebuild X", "start a clone", "make my version of X",
  "where are we", "what's next", "resume the clone", or when any clonekit-*
  skill is named without an existing project.
license: MIT
compatibility: Requires Python 3.8+ and bash for the bundled ./bin/replica tools.
metadata:
  version: "2.0.0"
  role: workflow-orchestrator
---

# clonekit

Eleven skills rebuild an app's features and flows, clean-room style. This
skill is the router: it decides which one runs and remembers where the work
stopped. Skills are the source of method; this skill only reads them,
follows them, and keeps state.

## Reads and writes

Reads:

- `clonekit/status.json` in the user's project (created here if missing)
- the artifacts named in the routing table below, to verify a stage really
  finished before trusting its state

Writes:

- `clonekit/status.json`

Tools: none. The orchestrator routes; the skills do the work.

## Step 1: bootstrap

If `clonekit/status.json` does not exist, ask the four discovery questions
(or propose answers and get one yes):

1. **Target scope**: which app, which platform, which slice? ("All of Notion"
   is not a slice; "pages, blocks and sharing" is.)
2. **Audience and angle**: an internal replacement, a vertical niche
   version, or a commercial product to sell?
3. **Preferred stack**: does the user have one, or should clonekit-architect
   recommend defaults?
4. **Clean-room confirmation**: features and flows are rebuilt fresh: no
   copied code, assets, logos, copy or private APIs.

Then:

1. Create `clonekit/` and write a fresh `status.json` (schema below) with
   every stage `pending`.
2. Set `recon` to `active` and hand off to **clonekit-recon**. A clone never
   starts from memory of what an app does; it starts from recon.
3. Recommend the early **clonekit-entrepreneur** run right after recon, so
   the USP shapes the architecture instead of following it.

## Step 2: read the state

```json
{
  "app": "name of your clone",
  "target": "the original app being studied",
  "platform": "web | ios | android | desktop",
  "created": "YYYY-MM-DD",
  "updated": "YYYY-MM-DD",
  "stages": {
    "recon":        {"state": "done", "artifacts": ["clonekit/recon.md"], "note": ""},
    "architect":    {"state": "done", "artifacts": ["clonekit/architecture.md"], "note": ""},
    "design":       {"state": "active", "artifacts": [], "note": ""},
    "build":        {"state": "pending", "artifacts": [], "note": ""},
    "backend":      {"state": "pending", "artifacts": [], "note": ""},
    "test":         {"state": "pending", "artifacts": [], "note": ""},
    "diff":         {"state": "pending", "artifacts": [], "note": ""},
    "entrepreneur": {"state": "pending", "artifacts": [], "note": ""},
    "brand":        {"state": "pending", "artifacts": [], "note": ""},
    "launch":       {"state": "pending", "artifacts": [], "note": ""},
    "deploy":       {"state": "pending", "artifacts": [], "note": ""}
  },
  "next": "design",
  "blocked": [],
  "gates": {
    "must_haves_complete": false,
    "zero_s1_s2_bugs": false,
    "parity_80": false,
    "brand_sweep_clean": false,
    "user_deployment_approved": false
  }
}
```

State values: `pending | active | done | blocked | skipped`. `next` holds the
stage name (the `clonekit-<next>` skill handles it). Keep the file small; one
entry per stage, artifacts as paths.

## Step 3: route the request

Match the request, then read that skill's `SKILL.md` and follow it. The
pipeline order is recon -> architect -> design -> build -> backend -> test ->
diff -> entrepreneur -> brand -> launch -> deploy, but requests jump freely:

| the user says (or means) | route to | reads |
| --- | --- | --- |
| clone / rebuild / reverse engineer / map an app; no status file | clonekit-recon | `clonekit/recon.md` |
| stack, schema, database, API, plan the build | clonekit-architect | `clonekit/architecture.md` |
| match the design, tokens, colours, components | clonekit-design | `clonekit/design/` |
| build it, build screen S07, implement a flow | clonekit-build | `clonekit/build-log.md` |
| login, auth, Stripe, payments, emails, integrations | clonekit-backend | `clonekit/backend.md` |
| test, QA, find bugs, write e2e tests | clonekit-test | `clonekit/bugs.md` |
| how close, compare, parity, what's missing | clonekit-diff | `clonekit/parity.md` |
| reviews, what users hate, positioning, the gap (best run right after recon) | clonekit-entrepreneur | `clonekit/fixes.md` |
| name it, rebrand, logo, check for leftovers | clonekit-brand | `clonekit/brand.md` |
| landing page, pricing, store listing | clonekit-launch | `clonekit/launch/` |
| deploy, ship, domain, production | clonekit-deploy | `clonekit/deploy.md` |
| where are we, what's next, resume | stay here | `clonekit/status.json` |

Mid-pipeline jumps are normal. "Add payments" runs clonekit-backend now even
if design is active; record the jump by setting the target stage `active` and
putting the interrupted stage back to `pending` with a `note`.

## Step 4: verify before you trust

Before treating a stage as `done`, check its artifacts exist (the "reads"
column above). A state file that claims done with no `recon.md` is wrong:
fix the state, then run the missing stage.

Flip a `gates` entry only with evidence: `parity_80` and
`must_haves_complete` from `./bin/replica parity` output, `zero_s1_s2_bugs`
from `clonekit/bugs.md`, `brand_sweep_clean` from a `./bin/replica sweep`
exit 0, and `user_deployment_approved` only from the user's explicit yes.

## Rules

- **Route, then follow.** Never paraphrase a skill from memory: read its
  `SKILL.md` file and do what it says.
- **Never mark a stage done without its artifacts.** Blocked stages get a
  `note` saying what is missing.
- **New project, no recon map -> recon.** Planning or building from memory
  is how half the app goes missing.
- **Confirm at three checkpoints**, in plain words, before moving on: after
  recon, "Confirm this feature perimeter before schema generation?"; after
  test and diff, "All core flows pass. Ready to rebrand and wipe target
  references?"; before deploy, paste the preflight report and ask for the go.
- **The deploy gate is not optional.** clonekit-deploy refuses to ship until
  its preflight passes (tests, parity must-haves, rebrand sweep, listing).
- **Keep the state honest.** Percentages and scores come from the tools, not
  from vibes. A clone at 62% is at 62%.

## Done when

- [ ] `clonekit/status.json` exists, is valid JSON, and every stage is in a legal state
- [ ] the request is classified and the target skill is named to the user
- [ ] the target skill's `SKILL.md` has been read and is being followed (or, for "where are we", the state is reported with `next`)
- [ ] after the work finishes, `status.json` is updated: states, artifacts, `next`

## Handoff

Dispatch: read `.agents/skills/<target-skill>/SKILL.md` and execute it, then
update `clonekit/status.json` when it reports Done. For "where are we", stay
here: print each stage with its state, then run the `next` stage.
