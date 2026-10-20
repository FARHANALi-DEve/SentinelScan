# SentinelScan — Product and Technical Design

**Date:** 2026-10-16  
**Status:** Original MVP approved; followed by owner-requested v2 local-workspace extension (see `docs/superpowers/plans/2026-10-16-complete-workspace.md`)  
**Purpose:** A polished portfolio application demonstrating Python engineering, web security fundamentals, full-stack UI, reporting, and reliable testing.

## 1. User goal and project boundaries

Build a self-hosted **security posture scanner** for websites the operator owns or is authorized to assess. Results should be easy to understand and beautiful enough to demonstrate in a portfolio. The application is non-invasive: it checks public HTTP response headers, TLS certificate information, redirects, and a few defensive configuration indicators. It does not attempt penetration, password guessing, crawling, exploitation, or vulnerability probing.

The previously agreed stack is a Python FastAPI backend, React + Tailwind dark dashboard, persistent scan history, charts, downloadable PDF reports, and finding explanations. The owner runs Windows and has a recent Python 3 version. An onboarding README must include PowerShell instructions.

## 2. Delivery slices and explicit limits

### Slice A — working portfolio MVP (first downloadable ZIP)

- FastAPI application with OpenAPI docs and health endpoint.
- Security scanner that can run against **explicitly configured authorized target hosts only**; a built-in offline demo scan is available without configuring a live target.
- Per-scan checks: HTTPS and redirect behavior, core security headers (CSP, HSTS, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, frame protection), cookie flags when seen, certificate validity window and verification, and basic server information disclosure.
- Explain each check with severity, plain-language impact, evidence, and an actionable fix.
- Persist scans and findings in SQLite for local ease of use; allow PostgreSQL through a future database URL configuration.
- React responsive premium dark UI with scan initiation, clear progress/error states, history, details, severity counters and charts; real data from the API, seeded demo data for portfolio viewing.
- PDF report export, automated backend tests, front-end build verification, project README, `.env.example`, and a ZIP of source code.

### Slice B — future enhancements, **not claims of MVP completion**

- Per-user authentication and account isolation.
- Production PostgreSQL migrations and durable distributed scan workers.
- Optional LLM-powered explanations using a user-provided API key; no key required for MVP explanations.
- Deeper asset discovery, scheduled re-scans, email alerts and multi-tenant deployment.

## 3. Architecture and responsibilities

- `backend/app/main.py` — FastAPI app, request validation, CORS configuration and routes.
- `backend/app/models.py` — database models / DTOs for scans and findings.
- `backend/app/scanner.py` — bounded, read-only HTTP and TLS checks; does not write database rows.
- `backend/app/policy.py` — network safety policy; validates URLs/hosts and network resolution.
- `backend/app/storage.py` — persistence and scan state transitions.
- `backend/app/report.py` — PDF rendering from saved, normalized findings.
- `backend/app/demo.py` — deterministic offline demonstration results.
- `frontend/src/` — React/TypeScript components, API client, view state and charts; browser makes API calls only to backend.
- `backend/tests/` — behavior-level and security-policy tests using stubs/mock transport rather than scanning uncontrolled live sites.

API shape:

- `GET /api/health` → service status.
- `POST /api/scans` → `{ "target": "https://authorized.example" }`, rejects unauthorized hosts and malformed URLs; returns scan id/status.
- `POST /api/scans/demo` → creates an offline seeded demonstration scan.
- `GET /api/scans` → recent history.
- `GET /api/scans/{id}` → individual scan, detailed findings, summary and status.
- `GET /api/scans/{id}/report.pdf` → downloadable report, generated from saved results.

For the first MVP, a scan can execute within an API request for predictable local behavior with bounded timeout. The UI must show a loading state until a response comes back. Workers are a later scaling feature, not implicitly promised as deployed in the MVP.

## 4. Safety and abuse resistance

- Live scans are **disabled until** `ALLOWED_TARGET_HOSTS` is configured by the developer/operator; allow only specific exact hosts, not wildcards by default.
- Only `http` and `https` schemes, only standard ports (80/443), no embedded credentials, no fragments, and no arbitrary proxy usage.
- Independently reject loopback, private, link-local, multicast, unspecified, reserved, and cloud metadata IP addresses, for both IPv4 and IPv6. Resolve DNS immediately before connection; fail closed if any resolved address violates the policy. Consider DNS rebinding: tie the validation to the actual destination connection in implementation/tests, or use an explicit documented security constraint if the transport cannot guarantee it.
- Redirects are disabled by default, with manual redirect inspection for at most 3 safe hops if desired; each redirect destination must be independently checked before a request.
- Restrict maximum HTTP response body bytes, connection/read timeouts, and number of network requests per scan. Do not download page resources, submit forms, fuzz endpoints, or enumerate paths.
- Only user-authorized websites are suitable targets. The demo path never reaches a network.
- Avoid logging sensitive header values; evidence shown to the user is bounded and redacted where appropriate.
- All persisted data remains local by default. No scan telemetry is transmitted to an external service.

## 5. Finding system and score

Every finding has a stable `check_id`, `title`, `severity` (`critical`, `high`, `medium`, `low`, `info`, `pass`), `description`, `evidence`, `recommendation`, and category. A documented score starts at 100 and subtracts weighted penalties for failed checks (high 20, medium 10, low 5; capped at 0). A score reflects checked configuration indicators only; it is **not** a guarantee of website security or a penetration-test rating. Reports must display that limitation clearly.

## 6. Visual design

A premium dark security operations aesthetic: graphite/navy surfaces, restrained cyan/teal highlights, readable white typography, card-based metric summaries, severity distribution and score trend chart, scan history table, findings sorted by severity, mobile navigation, and useful empty/loading/error states. Prefer polished clarity over purely decorative animation. Every chart must be grounded in actual results or visibly identified demo data.

## 7. Error handling and reliability

- Validation errors are actionable 4xx responses; unreachable targets and TLS failures produce a completed scan with relevant warning/error findings rather than a false success.
- The browser clearly distinguishes demo data from real authorized scans.
- Timeout and network failures have safe, bounded retry or clear messaging; no infinite retries.
- The app starts locally without needing cloud credentials, external authentication, or a paid AI API.

## 8. Test and acceptance criteria

1. Backend unit/API tests pass using deterministic simulated HTTP/TLS inputs.
2. Security-policy tests reject localhost, internal IPs, URL userinfo, disallowed hosts, custom ports, metadata IPs, and unsafe redirects/rebinding-like cases.
3. A clean local setup launches API and dashboard with documented Windows PowerShell commands.
4. A user can create a demo scan, inspect its individual findings and score, reload the page, see the saved history, and download a nonempty PDF.
5. A user can configure and scan an authorized public host without enabling arbitrary-host scanning.
6. The front-end production build succeeds and uses environment-controlled API origin.
7. README documents scope, target consent, security limitations, architecture, tests, and portfolio screenshots instructions.
8. The ZIP includes actual source and setup files, not compiled-only artifacts or placeholders masquerading as features.

## 9. Decisions and alternatives

- **SQLite first, not PostgreSQL-only:** minimizes setup friction on Windows; PostgreSQL support is a follow-up.
- **React frontend + FastAPI backend, rather than Python-only UI:** proves cross-stack experience and suits the originally proposed dashboard.
- **Rule-based finding explanations, not pretend AI:** useful offline and truthful; an actual LLM integration requires opt-in configuration in Slice B.
- **Authorized-host allowlist, not open scanning:** protects from Server-Side Request Forgery and unintended third-party scanning.
- **Synchronous bounded scan for MVP, not background queue:** simpler correctness, durable job scheduling later.

## 10. Review request

Please approve this written spec or request changes. After approval, the next Superpowers stage is a file-by-file implementation plan and execution-method selection. Coding should not be presented as completed until build/test results have been verified.
