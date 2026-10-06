---
name: clonekit-deploy
description: >-
  Ships an app clone live on the user's own domain: a preflight gate (tests
  green, parity must-haves done, rebrand sweep clean, listing linted, legal
  pages up), production database and env vars, the host, DNS records for the
  domain and for email, Stripe live mode, OAuth redirects, monitoring, and
  mobile builds to TestFlight and Play. Use when the user says "deploy it",
  "ship it", "put it live", "connect my domain", "go to production",
  "publish the app", or after /clonekit-launch.
license: MIT
compatibility: Requires Python 3.8+ and bash for the bundled ./bin/replica tools.
metadata:
  version: "2.0.0"
  role: devops-release-engineer
---

# clonekit-deploy

Reads everything in `clonekit/`. Writes `clonekit/deploy.md` (the checklist in
`preflight.md` in this folder, filled in).

## Reads and writes

Reads:

Everything in `clonekit/`, the test suite, and the tool outputs

Writes:

- `clonekit/deploy.md` (the filled preflight: template `preflight.md` in this folder)

Tools: ./bin/replica parity, ./bin/replica sweep and ./bin/replica listing for the preflight gates

## The rules

- **Nothing goes live without the user's go.** Show the preflight results and
  ask.
- **The user buys and signs in.** You never buy a domain, enter a card, type a
  password or paste a live key. You write the exact DNS records,
  env var names and commands; the user does the account steps.
- **Not until it is rebranded.** The sweep must be clean. No exceptions.

## Step 1: preflight

Run every check and paste the results into `deploy.md`:

```bash
npx playwright test                                                  # clonekit-test
./bin/replica parity clonekit/features.csv --fail-under 80   # gate: 80+
./bin/replica sweep . --config clonekit/brand.json      # exit 0: clean
./bin/replica listing clonekit/launch/listing.json     # if shipping to stores
npm run build                                                        # production build passes
```

(Run `./bin/replica <command>` from the project root; the wrapper finds the tools wherever the pack is installed.)

Plus by hand: no open S1 or S2 bugs, privacy policy and terms pages live
(listing every processor), cookie banner if you use non-essential cookies in
the EU or UK, account deletion works, the favicon, titles and OG image are
yours.

Any failure stops the deploy. Say which and why.

## Step 2: production services

- A **separate production project** for the database (never the dev one),
  backups on, migrations run by the deploy, not by hand.
- Env vars set in the host for production, matching `.env.example`. Live
  keys only here.
- **Stripe**: switch to live mode, recreate products and prices, add the
  production webhook endpoint and its signing secret, test one real
  purchase and refund it.
- **OAuth**: add the production domain to every provider's redirect URIs and
  authorised origins. Google scopes that need verification must be approved,
  or only test users can sign in.
- **Email**: the sending domain verified with the provider.

## Step 3: host and domain

Default: Vercel for Next.js (Netlify, Cloudflare Pages, Fly or Render
otherwise). Connect the repo so `main` deploys and pull requests get preview
URLs.

The domain, after the user buys it at any registrar:

| record | name | value |
| --- | --- | --- |
| A | @ | the host's apex IP (Vercel: shown in the domain settings) |
| CNAME | www | the host's target (Vercel: `cname.vercel-dns.com`) |
| TXT | @ or a subdomain | the host's verification value, if asked |

Email DNS from the email provider: SPF (TXT), DKIM (CNAME or TXT), and a
DMARC record starting at `v=DMARC1; p=none; rua=mailto:you@yourdomain` then
tightened to `quarantine` once reports are clean. Without these, your
confirmation emails go to spam.

Pick one canonical host (apex or www) and redirect the other. HTTPS is
automatic on the hosts above; check it.

## Step 4: watch it

Error tracking (Sentry or the host's), uptime checks on the home page and the
core flow's API, logs kept, analytics (a privacy-friendly one avoids the
cookie banner), and an alert to the user's email or phone. Then do the core
flow on the live site yourself, and ask the user to do it on their phone.

## Step 5: mobile, if there is an app

Expo: `eas build` then `eas submit` to TestFlight and Play internal testing.
Native: archive in Xcode, upload to App Store Connect; Gradle bundle to Play
Console. The user owns the developer accounts ($99 a year for Apple, $25 once
for Google). Beta first, then review with the listing from clonekit-launch.

## Output

`clonekit/deploy.md` with every check and its result, the live URL, the DNS
records set, and what to watch in the first week. The clone is now an app
with your name on it.

## Done when

- [ ] Preflight all green: tests, no S1/S2, must-haves done, sweep clean, listing clean, production build
- [ ] Legal pages live with every processor listed; account deletion works
- [ ] Production database, env vars, Stripe live, OAuth redirects, verified sending domain
- [ ] DNS and HTTPS checked; monitoring and alerts on
- [ ] Core flow done on the live site, and the user has done it on their phone

## Handoff

Update `clonekit/status.json`: set `deploy` to `done`, list `clonekit/deploy.md` and the live URL, and clear `next`. The pipeline is finished: tell the user the app is live under their own name, and what to watch in the first week.
