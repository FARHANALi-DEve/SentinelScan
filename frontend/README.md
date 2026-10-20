# SentinelScan frontend

This is a React + TypeScript dashboard with a prebuilt offline-friendly bundle.

- **Run immediately:** from repository root, `python -m http.server 5173 --bind 127.0.0.1 --directory frontend/dist`, then open `http://localhost:5173`.
- **Edit source:** `frontend/src/app.tsx` and `frontend/src/styles.css`.
- **Rebuild:** install Node.js 20+ and run `cd frontend && npm install && npm run build`. This recompiles TypeScript and copies CSS and HTML. The vendor files are already present in `dist/vendor/`.
- **For non-Windows with global TypeScript compiler:** `bash frontend/build.sh`.
- **Configure backend URL:** click Settings in the sidebar (defaults to `http://localhost:8000`).

The runtime uses vendored legacy React UMD for local-only demonstration. Its components are class-based to keep the ZIP functional without relying on an npm runtime/development server. For production, replace this legacy runtime with current React and Vite, and re-test before deployment. Styling is bespoke CSS, rather than Tailwind, to avoid a separate CSS build dependency. SVG charts render actual API scan results.

## Version 2 owner workflow

The backend now requires first-run registration and bearer token authentication. The compiled dashboard includes login, logout, account settings, scan deletion, comparison, CSV/PDF authenticated downloads and audit activity. Browser tab sessionStorage holds the token until logout, expiration or tab closure. Do not expose the legacy bundled React runtime directly on the public internet; modernize the frontend before deployment.
