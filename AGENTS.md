# AGENTS.md

## What this is

clonekit rebuilds another app's features and flows, clean-room style. Eleven
pipeline skills, one orchestrator, six standard-library Python tools. This
file is the router for agents that do not load skills automatically.

## Router

For any request about cloning, rebuilding or reverse-engineering an app, and
for any question about the state of a clone project ("where are we",
"what's next"), do this:

1. Read `.agents/skills/clonekit/SKILL.md` and follow it. It maintains
   `clonekit/status.json` and routes to the right skill.
2. Skills are self-contained: if your environment cannot load a skill
   directory, read the target skill's `SKILL.md` directly and follow it as
   written. Templates, example specs and tools sit next to each SKILL.md.
3. Run tools from the project root with `./bin/replica <command> ...`, or
   directly with `python3 .agents/skills/<skill>/<tool>.py ...`.

## Skill index

| skill | path | use it when |
| --- | --- | --- |
| clonekit | `.agents/skills/clonekit/SKILL.md` | any clone request, "where are we", routing, resume |
| clonekit-recon | `.agents/skills/clonekit-recon/SKILL.md` | first step: map an app's screens, flows, data model |
| clonekit-architect | `.agents/skills/clonekit-architect/SKILL.md` | plan the stack, schema and API |
| clonekit-design | `.agents/skills/clonekit-design/SKILL.md` | rebuild colours, type, spacing, components as tokens |
| clonekit-build | `.agents/skills/clonekit-build/SKILL.md` | build screen by screen from the recon map |
| clonekit-backend | `.agents/skills/clonekit-backend/SKILL.md` | auth, database, payments, email, integrations |
| clonekit-test | `.agents/skills/clonekit-test/SKILL.md` | test plan, e2e tests, bug reports |
| clonekit-diff | `.agents/skills/clonekit-diff/SKILL.md` | parity score and layout diff against the original |
| clonekit-entrepreneur | `.agents/skills/clonekit-entrepreneur/SKILL.md` | read real reviews, fix what users hate, find the angle |
| clonekit-brand | `.agents/skills/clonekit-brand/SKILL.md` | name, palette, logo brief, voice, leftover sweep |
| clonekit-launch | `.agents/skills/clonekit-launch/SKILL.md` | landing page, pricing, store listing |
| clonekit-deploy | `.agents/skills/clonekit-deploy/SKILL.md` | preflight, production, DNS, ship |

## Ground rules

- Clean-room: rebuild functionality, never the original's code, assets,
  logos, copy or content. Public sources and the user's own account only.
- No invented reviews, quotes, numbers or testimonials. Every claim links to
  its source.
- The user creates accounts, keys and purchases. Never type a password, card
  or live key for them.
- Nothing ships until the rebrand sweep is clean and the user says go.
