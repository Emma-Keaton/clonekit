# clonekit

Twelve agent-neutral skills that rebuild any app: reverse-engineer it from
public sources, plan the stack, rebuild the design system, build it screen by
screen, wire the backend, test it, score it against the original, fix what
its users hate, rebrand it, launch it, and ship it on your own domain.

Works with every coding agent: Claude Code, opencode, Cursor, Cline, Qwen
Code, Gemini CLI, Codex, Copilot, and anything else that reads skill folders
or an `AGENTS.md`. One canonical skill tree, one install command, one router.

Based on [replica-skill](https://github.com/Jakeschincariol/replica-skill)
by Jake Schincariol (MIT): the eleven pipeline skills, the six tools and the
templates come from that work, rewritten here to be agent-neutral, given the
`clonekit` orchestrator and state file, a unified tool CLI, tests, and a
multi-agent installer.

## Install

```bash
git clone <your-clonekit-repo> clonekit
cd clonekit && ./install.sh
```

Run it from any project instead to install the skills there:

```bash
/path/to/clonekit/install.sh --agent claude,cursor,cline,qwen,gemini,opencode
```

Options: `--agent <list>` force targets instead of auto-detect, `--global`
also install to home-directory targets, `--copy` copy instead of symlink,
`--dry-run` show the plan, `--help` the rest. Re-running is idempotent; an
existing `AGENTS.md` gets a marked block appended after a `*.bak` backup and
is never otherwise modified.

| agent | what install.sh does |
| --- | --- |
| Claude Code | links skill folders into `.claude/skills/` |
| opencode | links skill folders into `.opencode/skills/` |
| Cursor | adds a pointer rule at `.cursor/rules/clonekit.mdc` |
| Cline | adds `.clinerules/clonekit.md` |
| Qwen Code | adds a pointer block to `QWEN.md` |
| Gemini CLI | adds a pointer block to `GEMINI.md` |
| Windsurf | adds a pointer block to `.windsurfrules` |
| Roo Code | adds `.roorules/clonekit.md` |
| Codex, Copilot, others | the `AGENTS.md` router, always written |
| no skills support at all | read any `SKILL.md` directly; each is self-contained |

## The twelve skills

| skill | what it does |
| --- | --- |
| `clonekit` | Orchestrator. Entry point for every request: reads `clonekit/status.json`, routes to the right skill, keeps state so any agent can resume. |
| `clonekit-recon` | Reverse-engineers the app from public pages: screens, flows, components, inferred data model, feature matrix, honest size estimate. |
| `clonekit-architect` | Plans the stack, database schema and API; orders the build as a vertical slice first. |
| `clonekit-design` | Rebuilds the design system as tokens (colour roles, type, spacing, components) with open assets, WCAG-checked. |
| `clonekit-build` | Rebuilds the app screen by screen from the recon map, all states, ticking the feature matrix. |
| `clonekit-backend` | Auth, database access rules, payments, email, jobs, integrations through official APIs only, security checklist. |
| `clonekit-test` | Test plan from the flows, Playwright specs, bug reports by severity, fix loop until no S1 or S2 is open. |
| `clonekit-diff` | Parity score from the feature matrix plus a layout diff that ignores colour; verdict and missing list in build order. |
| `clonekit-entrepreneur` | Reads real public reviews of the original, ranks what users hate with linked quotes, turns it into fixes and a positioning angle. |
| `clonekit-brand` | Names and rebrands your version: checks, palette, logo brief, voice, then sweeps the codebase for leftovers of the original. |
| `clonekit-launch` | Landing page on the angle, pricing against the original, store listing linted against the stores' rules. |
| `clonekit-deploy` | Preflight gate (tests, parity, sweep, listing), production setup, DNS records, ship when the user says go. |

## The pipeline

```
any request
    |
    v
clonekit  (orchestrator: clonekit/status.json, routing, resume)
    |
    recon -> architect -> design -> build -> backend -> test
           -> diff -> entrepreneur -> brand -> launch -> deploy
```

Each skill reads what the last one wrote in the `clonekit/` folder of the
user's project and updates `status.json` on handoff. Jumps are allowed and
normal: "how close is my clone?" runs `clonekit-diff` whenever it is asked.

Two rules from the v2 flow: run `clonekit-entrepreneur` right after recon so
the USP shapes the architecture (it still works after diff), and hold five
gates in `status.json` (parity 80+, must-haves done, zero S1/S2 bugs, clean
rebrand sweep, explicit user go), so build -> backend -> test -> diff loops
until everything passes before the rebrand starts.

## Tools

Six standard-library Python tools, no installs, none of them touch the
network. One CLI over all of them:

```bash
./bin/replica parity clonekit/features.csv                 # parity score + missing list
./bin/replica imgdiff original.png clone.png --out diff.png # layout diff, ignores colour
./bin/replica reviews clonekit/reviews.csv                 # what users hate, ranked, linked
./bin/replica contrast clonekit/design/tokens.json          # WCAG contrast on tokens
./bin/replica sweep . --avoid "Original App"                # anything of the original left?
./bin/replica listing clonekit/launch/listing.json          # store limits + copycat checks
./bin/replica doctor                                        # environment self-check
```

Each tool also runs directly with
`python3 .agents/skills/<skill>/<tool>.py --help`. Exit codes gate CI: `0`
clean or passing, `1` findings or a failed gate, `2` usage or setup error.

- **imgdiff** compares structure, not colour: both screenshots become edge
  maps scored on a grid, so the rebrand does not count against you.
- **parity** weights must (3), should (2), could (1), counts partial as half,
  and never scores what you left out on purpose or added yourself.
- **reviews** drops every row without a link; every quote it prints is
  verbatim from a row you supplied, with that row's URL.
- **sweep** finds the original's name, domains and colours anywhere in the
  code, including inside identifiers like `OriginalAppEmbed`, and blocks a
  deploy until clean.
- **listing** checks App Store and Google Play limits, ranking claims in the
  title, wasted keyword characters, and the original's name anywhere.

## Development

```bash
python3 -m unittest discover -s tests -v   # python works too
```

The suite covers every tool, the CLI wrapper, and the repository contract:
twelve skills with valid frontmatter and the Reads/Writes, Done when and
Handoff sections, no agent product names inside the skill tree, every skill
indexed in `AGENTS.md` and this README, every referenced companion file
present.

## Ground rules (kept from the original, on purpose)

- **Clean-room.** Rebuild functionality and UX patterns, never the target's
  source code, proprietary assets, logos, trademarks, copy or private APIs.
- **Public sources and the user's own account only.** Never scrape behind a
  login, never get past a paywall, never log into anyone else's account.
- **Rebrand before launch.** New name, palette, logo, words.
  `clonekit-deploy` will not ship until the sweep is clean.
- **Never fabricate.** No invented reviews, quotes, numbers or testimonials.
  Every claim carries a link and the sample size.
- **The user creates accounts, keys and purchases.** The agent never types a
  password, card or live key.
- **Check before you sell.** Run the trademark checks `clonekit-brand` lists
  and talk to a lawyer if there is money on the line. This is not legal
  advice.

## Credit

Built on [replica-skill](https://github.com/Jakeschincariol/replica-skill)
by Jake Schincariol, [opusjake.ai](https://opusjake.ai), MIT.

## License

MIT. See `LICENSE`, which retains the original copyright notice.
