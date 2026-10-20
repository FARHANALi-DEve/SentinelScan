# SentinelScan Complete Local Workspace — Implementation Plan

**Goal:** Extend the approved local portfolio scanner with a complete owner workflow: private onboarding/login, saved history management, report export, and a polished authenticated dashboard.

**Architecture:** Keep the existing FastAPI and SQLite stack with strongly permissioned scan destinations. Introduce a single-owner auth store (scrypt salted password hashes, revocable hashed bearer sessions, login lockout), protect scan and report endpoints, and connect the existing React UI to the authenticated API.

**Tech stack:** Python 3.10+, FastAPI, sqlite3, reportlab, bundled React + TypeScript + CSS; no cloud credentials needed.

**Spec:** docs/superpowers/specs/2026-10-16-sentinelscan-design.md; requested expansion beyond its original MVP scope.

**Constraints:** Live scanning only for operator-allowlisted public domains. Initial owner setup only from local client and approved origin; never ship a shared default password. Existing scanner safety regression tests must remain green.

**Task 1 — Auth:** tests for setup, login, session protection, lockout, logout, password change, and persistence; implement AuthStore and endpoints. Run backend suite.

**Task 2 — Data management:** tests for authenticated CSV and delete, audit action records; implement backend routes, storage methods. Run suite.

**Task 3 — UI:** create setup and login forms, secure token handling, accessible logout, password update, PDF/CSV downloads with bearer credentials, history delete and comparison. Rebuild, run smoke tests and verify responsive layouts.

**Task 4 — Packaging:** update README/quick-start/limitations and screenshot, run full suite, package only source+working dist without test databases or secrets, extract+check ZIP integrity.

**Review focus:** unauthorized API calls and PDFs; first-user setup race and remote setup; lockout timing, session expiry and revocation; data deletion persistence; CSV formula injection; stale browser sessions; demo versus live labels.
