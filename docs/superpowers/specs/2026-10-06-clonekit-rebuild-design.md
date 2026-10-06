# clonekit rebuild -- design spec

Date: 2026-10-06
Status: approved in brainstorming (4/4 sections)
Source: `jakeschincariol-replica-skill.txt` (Replica skill pack by Jake Schincariol, MIT)

## Goal

Rebuild the Replica skill pack as **clonekit**: an agent-neutral app-cloning
skill pack that works with every coding agent, with an orchestrator that
routes requests, hardened Python tools, one-command multi-agent install, and
a new GitHub repository.

## Decisions made during brainstorming

| Decision | Choice |
| --- | --- |
| Delivery | Cross-agent skills standard: canonical `.agents/skills/` + `AGENTS.md` router + install script |
| Target agents | All that read skills or markdown: Claude Code, opencode, Cline, Qwen Code, Gemini CLI, Cursor, Codex/Copilot, ... |
| Pack name | `clonekit` (skills `clonekit`, `clonekit-recon`, ...; user workspace folder `clonekit/`) |
| Structure | Approach A: one canonical tree, install script links/copies into each agent |
| Credit | MIT retained; original copyright in LICENSE; README credit section |
| Publish | New GitHub repo `clonekit` (visibility and gh auth confirmed at push time) |

## Repository layout

Repository root is this project root. The source txt stays out of the repo
(gitignored) and is reference material only.

```
AGENTS.md                      # router any agent can read
README.md                      # quickstart, skill/tool tables, install matrix, credit, fine print
LICENSE                        # MIT, original copyright (c) 2026 Jake Schincariol retained
.gitignore
.agents/skills/                # canonical, portable skill tree
  clonekit/SKILL.md            # NEW: orchestrator (router)
  clonekit-recon/     SKILL.md + recon-map.md + features.csv
  clonekit-architect/ SKILL.md + architecture.md
  clonekit-design/    SKILL.md + tokens.json + contrast.py
  clonekit-build/     SKILL.md
  clonekit-backend/   SKILL.md
  clonekit-test/      SKILL.md + test-plan.md + bug-report.md + e2e.example.spec.ts
  clonekit-diff/      SKILL.md + imgdiff.py + parity.py
  clonekit-entrepreneur/ SKILL.md + reviews.py + themes.json
  clonekit-brand/     SKILL.md + sweep.py
  clonekit-launch/    SKILL.md + listing.py + listing.example.json
  clonekit-deploy/    SKILL.md + preflight.md
bin/replica                    # unified CLI wrapper over the Python tools (bash)
install.sh                     # one-command multi-agent install (bash)
tests/                         # ported + new tests
docs/superpowers/specs/        # this spec
```

## Component design

### 1. Orchestrator skill `clonekit`

Entry point for any request: "clone app X", "add payments", "where are we?",
"what's next?".

- Maintains `clonekit/status.json` in the user's project:

```json
{
  "app": "name of the clone",
  "target": "original app being studied",
  "platform": "web | ios | android | desktop",
  "created": "YYYY-MM-DD",
  "updated": "YYYY-MM-DD",
  "stages": {
    "recon":         {"state": "done", "artifacts": ["clonekit/recon.md"], "note": ""},
    "architect":     {"state": "active", "artifacts": [], "note": ""},
    "design":        {"state": "pending", "artifacts": [], "note": ""},
    "build":         {"state": "pending", "artifacts": [], "note": ""},
    "backend":       {"state": "pending", "artifacts": [], "note": ""},
    "test":          {"state": "pending", "artifacts": [], "note": ""},
    "diff":          {"state": "pending", "artifacts": [], "note": ""},
    "entrepreneur":  {"state": "pending", "artifacts": [], "note": ""},
    "brand":         {"state": "pending", "artifacts": [], "note": ""},
    "launch":        {"state": "pending", "artifacts": [], "note": ""},
    "deploy":        {"state": "pending", "artifacts": [], "note": ""}
  },
  "next": "architect",
  "blocked": []
}
```

- State values: `pending | active | done | blocked | skipped`.
- Routing rules:
  - No `clonekit/status.json` and no recon map -> start `clonekit-recon`
    (scope questions first).
  - Mid-pipeline jumps are allowed and normal: "add Stripe" -> `clonekit-backend`
    even while build is active; "how close am I" -> `clonekit-diff`;
    "name it" -> `clonekit-brand`.
  - Every skill's Handoff updates `status.json` (state, artifacts, `next`)
    and names the next skill to the user.
  - Deploy refuses to run while any stage needed by its preflight is not
    `done` (the deploy skill's preflight already enforces this with tools).
- Each stage in the pipeline order: recon -> architect -> design -> build ->
  backend -> test -> diff -> entrepreneur -> brand -> launch -> deploy.

### 2. Rewrite rules for all 12 skills

Applied to every `SKILL.md`:

1. **Agent-neutral voice.** No agent product names in skill bodies. Banned
   in `.agents/skills/**` (regex, enforced by tests): `Claude`,
   `Claude Code`, `\bCursor\b`, `Copilot`, `\bCline\b`, `Qwen`,
   `Gemini CLI`, `\bopencode\b`, `Windsurf`, `Aider`. Agent names appear
   only in README and install.sh.
2. **Fixed contract**, in this order:
   - YAML frontmatter: `name` (folder name) and `description` written for
     embedding-based discovery (trigger phrases: what the user says).
   - `# <name>` heading and a one-paragraph purpose.
   - **Reads / Writes**: exact file paths in the user's project
     (`clonekit/...`) and companion files in the skill folder.
   - **Steps**: numbered, same methodology as the original pack.
   - **Rules**: the hard constraints (clean-room, no fabrication, user
     creates accounts, etc.) kept in substance from the original.
   - **Done when**: checkable list.
   - **Handoff**: update `clonekit/status.json`, name the next skill.
3. **Progressive disclosure.** SKILL.md <= ~180 lines. Templates, examples
   and long tables stay in companion files referenced by path.
4. **Tool invocation** documented as `replica <subcommand> ...` first, with
   the direct `python3 path/to/tool.py ...` fallback one line below.
5. **Methodology preserved.** The original's steps, guardrails and legal
   fine print are kept in substance; wording is rewritten, not copied.
   The workspace folder changes from `replica/` to `clonekit/`, and tool
   paths inside skill text point at `.agents/skills/<skill>/<tool>.py`
   relative to the repo (or the `replica` wrapper).

### 3. Python tools

Six tools ported from the source with behavior, flags and exit codes
preserved (0 = pass/clean, 1 = findings/fail, 2 = usage error):

| Command | Tool | Job |
| --- | --- | --- |
| `replica parity` | clonekit-diff/parity.py | feature parity score + missing list |
| `replica imgdiff` | clonekit-diff/imgdiff.py | layout/pixel screenshot diff |
| `replica contrast` | clonekit-design/contrast.py | WCAG contrast on tokens |
| `replica reviews` | clonekit-entrepreneur/reviews.py | rank what users hate, linked quotes |
| `replica sweep` | clonekit-brand/sweep.py | find leftovers of the original |
| `replica listing` | clonekit-launch/listing.py | store listing lint |
| `replica doctor` | new | environment self-check |

`bin/replica` (bash, Git Bash compatible):

- Picks `python3` if present, else `python`; fails with a clear message if
  neither or Python < 3.8.
- Resolves its own real path (symlink-safe) to find `.agents/skills/`, so it
  works after install into agent folders.
- Passes all arguments through to the tool; tools stay directly runnable.

### 4. Tests

Runner: `python -m unittest discover -s tests -v` (or `python3`).

- Ported (paths adapted via `tests/_load.py` against `.agents/skills/`):
  `test_contrast_listing.py`, `test_imgdiff.py`, `test_parity.py`,
  `test_reviews.py`, `test_sweep.py`.
- Rewritten: `test_repo.py` --
  - 12 skill folders exist, each with valid frontmatter (`name` equals
    folder, `description` present and substantial).
  - No banned agent names in any file under `.agents/skills/`.
  - Every skill is listed in `AGENTS.md` and `README.md`.
  - Every companion file referenced inside a SKILL.md exists on disk.
- New: `test_cli.py` -- wrapper subcommand dispatch, `doctor` exit code,
  missing-interpreter error path (where testable).

### 5. `install.sh`

Bash, runs on macOS, Linux and Windows (Git Bash).

- Agent table (exact target paths verified by research during
  implementation; table lives in install.sh and mirrors in README):

| Agent | Detection | Action |
| --- | --- | --- |
| Claude Code | `.claude/` or `--agent claude` | link/copy skills into `.claude/skills/` |
| opencode | `.opencode/` / config dir | link/copy skills into its skills dir |
| Cline | `.clinerules/` | append pointer block to its rules file |
| Qwen Code | `.qwen/` or `QWEN.md` | append pointer block |
| Gemini CLI | `.gemini/` or `GEMINI.md` | append pointer block |
| Cursor | `.cursor/` | append pointer block / rules |
| Codex / Copilot / any | `AGENTS.md` | write/append router block |

- Flags: `--agent <list>`, `--global` (home-dir targets), `--copy`
  (force copies), `--dry-run`, `--help`. Default: detect in current
  project, link each skill folder, ensure AGENTS.md router.
- Symlink probe: create a test link; if the platform refuses (some Windows
  setups), fall back to copies with a notice.
- Idempotent: pointer blocks are delimited by
  `<!-- clonekit:begin -->` / `<!-- clonekit:end -->` markers; re-running
  replaces the block, never duplicates it. An existing AGENTS.md is backed
  up (`AGENTS.md.bak`) before its block is added, and never otherwise
  modified.

### 6. `AGENTS.md`

Short router (~40 lines): what clonekit is, "any clone/rebuild request ->
read `.agents/skills/clonekit/SKILL.md` and follow it", the skill index
table with paths, and a fallback for agents without skill support ("read
the SKILL.md directly; it is self-contained").

### 7. `README.md`

Sections: what it is, one-command install, pipeline diagram
(`clonekit` orchestrator -> 11 stages), skill table (name, what it does),
tool table with example commands, per-agent install matrix, development
(tests), credit ("Based on replica-skill by Jake Schincariol, MIT"), fine
print (clean-room, no scraping behind logins, rebrand before launch, no
fake reviews, check trademarks, not legal advice).

### 8. Publishing

1. `git init -b main`, `.gitignore` (source txt, `__pycache__/`, `*.pyc`,
   `AGENTS.md.bak*`).
2. Logical commits: spec -> skills -> tools + tests -> install + docs.
3. Confirm gh auth and repo visibility with the user, then
   `gh repo create clonekit --public|--private --source . --push`.

## Verification (definition of done)

1. `python -m unittest discover -s tests -v` -- all tests pass.
2. Every tool smoke-tested through `bin/replica` with fixture data; exit
   codes verified (0 clean, 1 findings, 2 usage).
3. `bin/replica doctor` exits 0 on this machine.
4. `install.sh --dry-run` output reviewed; a real run against temp agent
   directories creates the expected links/pointer blocks; a second run is
   idempotent; backup created when AGENTS.md exists.
5. Skill checks green: 12 skills, valid frontmatter, indexed in AGENTS.md
   and README, no banned agent names in bodies, all referenced companion
   files exist.
6. LICENSE carries the original copyright notice; README has the credit
   section.
7. Repository pushed to GitHub; URL shared with the user.

## Out of scope

- Changing scoring algorithms or tool behavior beyond portability fixes.
- New skill categories beyond the orchestrator.
- CI (GitHub Actions) -- possible follow-up, not part of this build.
- Content of the original `jakeschincariol-replica-skill.txt` being
  committed to the new repo (kept local as reference).
