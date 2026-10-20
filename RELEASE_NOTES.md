# SentinelScan v2 — Complete Local Workspace

This is a new archive, not a copy of the earlier MVP ZIP.

## Added since the first ZIP

- First-run private owner setup, strong password hashing, login, logout and 8-hour revocable sessions.
- Login lockout, change password, and a local password recovery CLI.
- Authorization checks for all scan endpoints and PDF/CSV report downloads.
- Delete saved assessments and review activity logs.
- Comparison page for two stored scan scores.
- Secure client-side downloads with authorization headers and escaped spreadsheet CSV values.
- Updated Windows instructions, API reference and security considerations.
- Regression tests for authentication, permissions, revocation, expiry and data operations.
- Updated real desktop/mobile dashboard screenshots and mobile login screenshot.

## Verification

- Backend suite: 55 tests passing (policy, scanning, API, authentication, persistence and reports).
- Frontend build and bundled-asset smoke checks passing.
- Browser UI controls exercised in a local, in-memory FastAPI bridge (setup, demo scan, comparison, CSV/PDF, activity, delete, mobile login/dashboard). Browser direct network navigation was restricted by the test environment.

## Still not included / not claimed

- Public hosting, SaaS billing, multi-tenant accounts, cloud deployment or a production security certification.
- Modern React migration or hardened internet deployment; vendored React 16 runtime is for an offline local portfolio workflow.
- Intrusive vulnerability exploitation or scans of domains outside the explicitly configured operator allowlist.
