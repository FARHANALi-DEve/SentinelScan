"""Portable asset smoke checks; run after frontend/build.sh."""
from pathlib import Path

base=Path(__file__).resolve().parent
html=(base/'index.html').read_text()
app=(base/'dist/app.js').read_text()
css=(base/'dist/styles.css').read_text()
assert 'SentinelScan' in html
assert 'ReactDOM.render' in app
assert '/api/scans/demo' in app
assert '/api/scans' in app
assert 'report.pdf' in app
assert 'Security overview' in app
assert 'OFFLINE DEMO PREVIEW' in app  # banner must not imply demo findings came from a live scan
assert '/api/auth/setup' in app
assert '/api/auth/login' in app
assert '/api/auth/logout' in app
assert '/api/auth/password' in app
assert '/api/reports/scans.csv' in app
assert 'Compare scans' in app
assert 'Activity log' in app
assert 'Permanently delete assessment' in app
assert '.auth-panel' in css
assert '.compare-selectors' in css
assert '@media' in css
assert (base/'dist/vendor/react.production.min.js').stat().st_size>5000
assert (base/'dist/vendor/react-dom.production.min.js').stat().st_size>80000
print('PASS: compiled React UI, API hooks, reports, responsive CSS and vendored runtimes')
