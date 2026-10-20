#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p dist/vendor
if ! command -v tsc >/dev/null 2>&1; then echo 'TypeScript compiler required: npm install -g typescript' >&2; exit 1; fi
tsc --target es2019 --lib dom,es2019 --jsx react --skipLibCheck --outFile dist/app.js src/app.tsx
cp src/styles.css dist/styles.css
cp index.html dist/index.html
python smoke_test.py
