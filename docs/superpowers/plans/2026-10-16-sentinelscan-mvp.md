# SentinelScan MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Deliver a runnable portfolio-grade authorized website security dashboard with offline demo scans, bounded live checks, saved history, and PDF exports.

**Architecture:** Python FastAPI API backed by SQLite, a DNS-pinned HTTP/TLS scanner with strict host allowlisting, deterministic offline demo, and a React/TypeScript frontend compiled to self-contained static assets. No external cloud credentials needed.

**Tech Stack:** Python 3.10+, FastAPI, http.client/ssl/sqlite3, reportlab, pytest; React, TypeScript, CSS/SVG charts.

**Spec:** `docs/superpowers/specs/2026-10-16-sentinelscan-design.md`

## Global Constraints
- Live scans disabled unless ALLOWED_TARGET_HOSTS lists the exact authorized public host.
- No arbitrary URL scanning, private addresses, unsafe ports, credential URLs, proxy use or unvalidated redirects.
- Local-first SQLite persistence; true network-free demo mode.
- Offline friendly setup with Windows PowerShell commands.
- Scores describe checked configuration indicators only, not comprehensive vulnerability scanning.

## Review Focus
- DNS rebind between validation/connection: pinned IP must be used at connection time.
- Redirect toward non-allowlisted host: fail closed before subsequent hop.
- Malicious cookie/header evidence: limit and redact data exposed in stored results.
- Fresh database and concurrent FastAPI requests: stable persistence without corruption.
- Offline demo + static UI when services are disconnected: clear error and recovery UI.

---

### Task 1: URL and network policy
**Files:** `backend/app/policy.py`, `backend/tests/test_policy.py`
**Interfaces:** `TargetPolicy.validate(raw_url)->ValidatedTarget`, `TargetPolicy.resolve(hostname)->str`.
- [x] Write policy tests for safe normalized targets and rejected schemes, ports, credentials, non-allowlisted hosts, private IPs and unsafe redirects.
- [x] Run policy tests RED (missing function/classes).
- [x] Implement exact-host policy and fail-closed DNS resolution.
- [x] Run tests GREEN; run full backend suite; commit.

### Task 2: Findings, scanner and demo
**Files:** `backend/app/scanner.py`, `backend/app/demo.py`, `backend/tests/test_scanner.py`
**Interfaces:** `scan_target(target, policy, transport=None)->dict`, `demo_result()->dict`, `evaluate_headers(headers, scheme, tls_info)->list[dict]`.
- [x] Write failing tests for header checks, score and deterministic demo, TLS failures and bounded redirects.
- [x] Run targeted tests RED.
- [x] Implement read-only checks, pinned address connections, and structured findings.
- [x] Run targeted tests GREEN and entire backend suite; commit.

### Task 3: Persistence, API and PDF
**Files:** `backend/app/storage.py`, `backend/app/main.py`, `backend/app/report.py`, `backend/tests/test_api.py`, `backend/requirements.txt`, `.env.example`.
**Interfaces:** API health, create demo/live scan, history, detail and report endpoints per spec; report uses saved data.
- [x] Write failing API tests with temporary DB and simulated scanner, including invalid target and persistent history.
- [x] Run API tests RED.
- [x] Implement storage/routes/report and configurations.
- [x] Run targeted tests GREEN, all backend tests; commit.

### Task 4: Dashboard and portable static build
**Files:** `frontend/src/app.tsx`, `frontend/src/types.d.ts`, `frontend/src/styles.css`, `frontend/index.html`, `frontend/dist/`, `frontend/build.sh`, `frontend/README.md`.
**Interfaces:** Browser requests API endpoints, uses data types documented in backend; demo/live, history, details, PDF.
- [x] Define smoke assertions for the exported dashboard markup/source and a production bundle.
- [x] Run check RED before UI files exist.
- [x] Implement polished responsive React UI and CSS, charts from real data, error/loading states, and offline local static bundle.
- [x] Run frontend compile/static smoke checks GREEN; commit.

### Task 5: Integration, documentation and delivery
**Files:** `README.md`, `start-backend.ps1`, `start-frontend.ps1`, `backend/tests/test_end_to_end.py`, `.gitignore`.
**Interfaces:** Reproducible local startup; demo report generated end-to-end; ZIP source delivery.
- [x] Add failing end-to-end checks for history, details, PDFs and offline smoke behavior.
- [x] Verify RED then implement necessary fixes.
- [x] Run full backend suite, TS compile, browser/API smoke tests, package ZIP, inspect ZIP content; commit.

**Execution:** In-session implementation requested explicitly by the owner with no further checkpoints. Any features beyond the approved MVP (authentication, cloud queues, LLM) are not claimed as implemented.

## Final verification evidence
- 44 backend tests passed; frontend TS compile and static smoke checks passed.
- Browser rendering verified at desktop 1440px and mobile 390px using deterministic mocked API responses (no JS console errors).
- Local HTTP API health/demo/history/detail/PDF flow exercised; PDF rendered successfully on two pages.
- Live scans against real third-party websites are intentionally **not** exercised.
