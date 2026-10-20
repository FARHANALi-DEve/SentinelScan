// @ts-nocheck
/* SentinelScan: dependency-light React/TypeScript dashboard, compatible with locally bundled React 16. */
const API_STORAGE_KEY = 'sentinelscan.apiBase';
const DEFAULT_API = 'http://localhost:8000';
const TOKEN_KEY = 'sentinelscan.ownerSession';
const NAV = [
    { id: 'overview', icon: 'grid', text: 'Overview' },
    { id: 'history', icon: 'clock', text: 'Scan history' },
    { id: 'findings', icon: 'shield', text: 'Findings' },
    { id: 'reports', icon: 'file', text: 'Reports' },
    { id: 'compare', icon: 'activity', text: 'Compare scans' },
    { id: 'activity', icon: 'clock', text: 'Activity log' },
];
const severityOrder = ['critical', 'high', 'medium', 'low', 'info', 'pass'];
const formatDate = (v) => v ? new Date(v).toLocaleString(undefined, { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : '—';
const displayHost = (v) => { try {
    return new URL(v).hostname;
}
catch (_) {
    return v;
} };
const clip = (s, n = 55) => s.length > n ? s.substring(0, n - 1) + '…' : s;
const percent = (n, d) => d > 0 ? Math.round(n / d * 100) : 0;
function scoreClass(n) { return n >= 80 ? 'good' : n >= 55 ? 'caution' : 'danger'; }
function Icon({ name, size = 19 }) {
    const iconPaths = {
        grid: React.createElement("g", null,
            React.createElement("rect", { x: "3", y: "3", width: "7", height: "7", rx: "1.5" }),
            React.createElement("rect", { x: "14", y: "3", width: "7", height: "7", rx: "1.5" }),
            React.createElement("rect", { x: "3", y: "14", width: "7", height: "7", rx: "1.5" }),
            React.createElement("rect", { x: "14", y: "14", width: "7", height: "7", rx: "1.5" })),
        clock: React.createElement("g", null,
            React.createElement("circle", { cx: "12", cy: "12", r: "9" }),
            React.createElement("path", { d: "M12 7v5l3.5 2" })),
        shield: React.createElement("g", null,
            React.createElement("path", { d: "M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11z" }),
            React.createElement("path", { d: "m9 12 2 2 4-4" })),
        file: React.createElement("g", null,
            React.createElement("path", { d: "M6 2h8l5 5v14a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V3a1 1 0 0 1 1-1z" }),
            React.createElement("path", { d: "M14 2v6h5M8 13h8M8 17h6" })),
        settings: React.createElement("g", null,
            React.createElement("circle", { cx: "12", cy: "12", r: "3" }),
            React.createElement("path", { d: "M19.5 15.5 21 17l-3.5 3.5-1.5-1.5M4.5 8.5 3 7l3.5-3.5L8 5M12 2v3M12 19v3M2 12h3M19 12h3" })),
        globe: React.createElement("g", null,
            React.createElement("circle", { cx: "12", cy: "12", r: "9" }),
            React.createElement("path", { d: "M3 12h18M12 3c-5 5-5 13 0 18M12 3c5 5 5 13 0 18" })),
        search: React.createElement("g", null,
            React.createElement("circle", { cx: "10.5", cy: "10.5", r: "6.5" }),
            React.createElement("path", { d: "m15.5 15.5 5 5" })),
        arrow: React.createElement("path", { d: "M5 12h14m-7-7 7 7-7 7" }),
        down: React.createElement("g", null,
            React.createElement("path", { d: "M12 4v13m-5-5 5 5 5-5M4 20h16" })),
        refresh: React.createElement("g", null,
            React.createElement("path", { d: "M20 11a8 8 0 1 0-2 5M20 4v7h-7" })),
        bolt: React.createElement("path", { d: "m13 2-9 12h7l-1 8 10-12h-7l0-8z" }),
        check: React.createElement("path", { d: "m5 12 4 4L19 6" }),
        alert: React.createElement("g", null,
            React.createElement("path", { d: "M12 3 2 21h20L12 3z" }),
            React.createElement("path", { d: "M12 9v5M12 17h.01" })),
        menu: React.createElement("path", { d: "M4 7h16M4 12h16M4 17h16" }),
        close: React.createElement("path", { d: "M5 5l14 14M19 5 5 19" }),
        lock: React.createElement("g", null,
            React.createElement("rect", { x: "5", y: "11", width: "14", height: "11", rx: "2" }),
            React.createElement("path", { d: "M8 11V7a4 4 0 0 1 8 0v4" })),
        info: React.createElement("g", null,
            React.createElement("circle", { cx: "12", cy: "12", r: "9" }),
            React.createElement("path", { d: "M12 11v5M12 7h.01" })),
        external: React.createElement("g", null,
            React.createElement("path", { d: "M13 5h6v6M19 5l-9 9" }),
            React.createElement("path", { d: "M19 13v5a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h5" })),
        activity: React.createElement("path", { d: "M2 12h4l3-8 5 16 3-8h5" }),
        trash: React.createElement("g", null,
            React.createElement("path", { d: "M4 7h16M9 7V4h6v3M7 7l1 14h8l1-14M10 11v6M14 11v6" })),
        logout: React.createElement("g", null,
            React.createElement("path", { d: "M10 4H5v16h5M14 8l4 4-4 4M8 12h10" })),
    };
    return React.createElement("svg", { width: size, height: size, viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "1.7", strokeLinecap: "round", strokeLinejoin: "round", "aria-hidden": "true" }, iconPaths[name] || iconPaths.shield);
}
function Brand() { return React.createElement("div", { className: "brand" },
    React.createElement("div", { className: "brand-mark" },
        React.createElement(Icon, { name: "shield", size: 25 })),
    React.createElement("div", null,
        React.createElement("div", { className: "brand-name" },
            "SENTINEL",
            React.createElement("span", null, "SCAN")),
        React.createElement("div", { className: "brand-sub" }, "SECURITY INTELLIGENCE"))); }
function Badge({ severity }) { return React.createElement("span", { className: 'badge badge-' + severity },
    React.createElement("span", { className: "badge-dot" }),
    severity === 'pass' ? 'Passed' : severity); }
function DotGrid() { return React.createElement("div", { className: "dotgrid" }); }
function ScoreRing({ score, size = 194 }) {
    const n = Math.max(0, Math.min(100, score || 0));
    const circumference = 2 * Math.PI * 80;
    return React.createElement("div", { className: 'score-ring ' + scoreClass(n), style: { width: size, height: size } },
        React.createElement("svg", { viewBox: "0 0 200 200", role: "img", "aria-label": 'Security posture score ' + n + ' out of 100' },
            React.createElement("circle", { cx: "100", cy: "100", r: "80", className: "ring-track" }),
            React.createElement("circle", { cx: "100", cy: "100", r: "80", className: "ring-value", strokeDasharray: circumference, strokeDashoffset: (circumference * (100 - n)) / 100, transform: "rotate(-90 100 100)" })),
        React.createElement("div", { className: "ring-text" },
            React.createElement("div", { className: "ring-number" },
                n,
                React.createElement("small", null, "/100")),
            React.createElement("div", { className: "ring-status" }, n >= 80 ? 'HEALTHY' : n >= 55 ? 'NEEDS ATTENTION' : 'AT RISK')));
}
function SectionHead({ eyebrow, title, right }) { return React.createElement("div", { className: "section-head" },
    React.createElement("div", null,
        React.createElement("div", { className: "eyebrow" }, eyebrow),
        React.createElement("h2", null, title)),
    right); }
function TrendChart({ scans }) {
    const chronological = [...scans].slice(0, 8).reverse();
    if (!chronological.length)
        return React.createElement("div", { className: "no-chart" }, "Run your first scan to see scoring history.");
    const points = chronological.map((s, i) => ({ x: 36 + i * (500 / Math.max(1, chronological.length - 1)), y: 170 - (s.score / 100) * 140, value: s.score, label: displayHost(s.target) }));
    const d = points.map((p, i) => (i ? 'L' : 'M') + p.x + ',' + p.y).join(' ');
    const fill = d + ' L' + points[points.length - 1].x + ',182 L' + points[0].x + ',182 Z';
    return React.createElement("div", { className: "chart-wrap" },
        React.createElement("svg", { viewBox: "0 0 565 215", "aria-label": "Score trend for recent scans", role: "img", className: "trend-svg" },
            React.createElement("defs", null,
                React.createElement("linearGradient", { id: "trendFill", x1: "0", y1: "0", x2: "0", y2: "1" },
                    React.createElement("stop", { offset: "0", stopColor: "#30dec7", stopOpacity: ".24" }),
                    React.createElement("stop", { offset: "1", stopColor: "#30dec7", stopOpacity: "0" }))),
            [30, 100, 170].map((y, i) => React.createElement("g", { key: i },
                React.createElement("line", { x1: "36", y1: y, x2: "545", y2: y, stroke: "#233b4b", strokeDasharray: "4 7" }),
                React.createElement("text", { x: "4", y: y + 4, fill: "#6d8c9a", fontSize: "11" }, 100 - i * 50))),
            React.createElement("path", { d: fill, fill: "url(#trendFill)" }),
            React.createElement("path", { d: d, fill: "none", stroke: "#37e0ca", strokeWidth: "3", strokeLinecap: "round", strokeLinejoin: "round" }),
            points.map((p, i) => React.createElement("g", { key: i },
                React.createElement("circle", { cx: p.x, cy: p.y, r: "5", fill: "#071b26", stroke: "#37e0ca", strokeWidth: "2.5" }),
                React.createElement("text", { x: p.x, y: "205", textAnchor: "middle", fontSize: "10", fill: "#76929e" },
                    "#",
                    i + 1)))),
        React.createElement("div", { className: "chart-bottom" },
            React.createElement("span", null, "Oldest scan"),
            React.createElement("span", null, "Most recent scan")));
}
function Distribution({ findings }) {
    const active = findings.filter(f => f.severity !== 'pass');
    const cats = {};
    active.forEach(f => cats[f.category] = (cats[f.category] || 0) + 1);
    const values = Object.entries(cats).sort((a, b) => b[1] - a[1]).slice(0, 5);
    if (!values.length)
        return React.createElement("div", { className: "quiet-empty" }, "No open findings for this scan.");
    const max = Math.max(...values.map((r) => r[1]));
    return React.createElement("div", { className: "distribution" }, values.map((pair, i) => React.createElement("div", { className: "dist-row", key: pair[0] },
        React.createElement("div", { className: "dist-head" },
            React.createElement("span", null, pair[0]),
            React.createElement("b", null, pair[1])),
        React.createElement("div", { className: "bar-track" },
            React.createElement("div", { className: 'bar-fill bar-' + i, style: { width: (pair[1] / max * 100) + '%' } })))));
}
function getStatus(f) { return f.severity === 'pass' ? 'pass' : f.severity === 'high' || f.severity === 'critical' ? 'high' : f.severity === 'medium' ? 'medium' : 'low'; }
function Findings({ scan, query = '', limit }) {
    if (!scan)
        return React.createElement("div", { className: "quiet-empty" }, "Choose a scan to inspect its findings.");
    const sorted = [...scan.findings].sort((a, b) => severityOrder.indexOf(a.severity) - severityOrder.indexOf(b.severity));
    const filtered = sorted.filter(f => (f.title + ' ' + f.category + ' ' + f.description).toLowerCase().includes(query.toLowerCase()));
    const shown = limit ? filtered.slice(0, limit) : filtered;
    return React.createElement("div", { className: "finding-list" }, shown.length ? shown.map((f, i) => React.createElement("details", { key: f.check_id + '-' + i, className: "finding-row" },
        React.createElement("summary", null,
            React.createElement("div", { className: 'finding-icon ' + getStatus(f) },
                React.createElement(Icon, { name: f.severity === 'pass' ? 'check' : 'alert', size: 17 })),
            React.createElement("div", { className: "finding-main" },
                React.createElement("strong", null, f.title),
                React.createElement("span", null, f.category)),
            React.createElement(Badge, { severity: f.severity }),
            React.createElement("span", { className: "chevron" }, "\u2304")),
        React.createElement("div", { className: "finding-details" },
            React.createElement("p", null, f.description),
            React.createElement("div", { className: "finding-meta" },
                React.createElement("b", null, "Evidence"),
                " ",
                f.evidence),
            React.createElement("div", { className: "finding-meta" },
                React.createElement("b", null, "Recommended fix"),
                " ",
                f.recommendation)))) : React.createElement("div", { className: "quiet-empty" }, "No findings matched your search."));
}
function HistoryTable({ scans, onSelect, selectedId, onDelete }) {
    if (!scans.length)
        return React.createElement("div", { className: "quiet-empty" }, "No scans yet. Launch a demo scan to populate your history.");
    return React.createElement("div", { className: "table-scroll" },
        React.createElement("table", { className: "history-table" },
            React.createElement("thead", null,
                React.createElement("tr", null,
                    React.createElement("th", null, "Target"),
                    React.createElement("th", null, "Type"),
                    React.createElement("th", null, "Date"),
                    React.createElement("th", null, "Score"),
                    React.createElement("th", null))),
            React.createElement("tbody", null, scans.map(s => React.createElement("tr", { key: s.id, className: s.id === selectedId ? 'selected-row' : '' },
                React.createElement("td", null,
                    React.createElement("button", { className: "target-button", onClick: () => onSelect(s.id) },
                        React.createElement("span", { className: "host-icon" },
                            React.createElement(Icon, { name: "globe", size: 16 })),
                        React.createElement("span", null,
                            React.createElement("b", null, clip(displayHost(s.target), 25)),
                            React.createElement("small", null,
                                "Scan #",
                                String(s.id).padStart(4, '0'))))),
                React.createElement("td", null, s.demo ? React.createElement("span", { className: "demo-label" }, "\u25CF Demo") : React.createElement("span", { className: "live-label" }, "\u25CF Live")),
                React.createElement("td", { className: "muted small" }, formatDate(s.scanned_at)),
                React.createElement("td", null,
                    React.createElement("span", { className: 'score-pill ' + scoreClass(s.score) },
                        s.score,
                        "/100")),
                React.createElement("td", null,
                    React.createElement("div", { className: "row-actions" },
                        React.createElement("button", { className: "icon-button", "aria-label": 'View scan ' + s.id, onClick: () => onSelect(s.id) },
                            React.createElement(Icon, { name: "arrow", size: 17 })),
                        onDelete ? React.createElement("button", { className: "icon-button delete-button", "aria-label": 'Delete scan ' + s.id, title: "Delete assessment", onClick: () => onDelete(s.id) },
                            React.createElement(Icon, { name: "trash", size: 16 })) : null)))))));
}
function AuthScreen({ mode, error, username, password, confirm, busy, onUsername, onPassword, onConfirm, onSubmit, onRetry }) {
    const checking = mode === 'checking';
    const setup = mode === 'setup';
    const unavailable = mode === 'offline';
    return React.createElement("div", { className: "auth-layout" },
        React.createElement("div", { className: "auth-ambient auth-ambient-one" }),
        React.createElement("div", { className: "auth-ambient auth-ambient-two" }),
        React.createElement("div", { className: "auth-brand" },
            React.createElement(Brand, null),
            React.createElement("span", null, "PRIVATE SECURITY OPERATIONS")),
        React.createElement("div", { className: "auth-panel" },
            React.createElement("div", { className: "auth-panel-icon" },
                React.createElement(Icon, { name: "shield", size: 30 })),
            React.createElement("div", { className: "eyebrow" }, "SENTINELSCAN / ACCESS CONTROL"),
            React.createElement("h1", null,
                checking ? 'Securing your workspace' : unavailable ? 'Backend unavailable' : setup ? 'Create your workspace' : 'Welcome back',
                React.createElement("span", { className: "heading-period" }, ".")),
            React.createElement("p", null, checking ? 'Checking your local account…' : unavailable ? 'Start the Python backend, then reconnect.' : setup ? 'Your first account will be the only owner. Choose a strong password to protect reports and scan history.' : 'Sign in to access your private scans, reports and security history.'),
            error ? React.createElement("div", { className: "auth-error" },
                React.createElement(Icon, { name: "alert", size: 17 }),
                error) : null,
            checking ? React.createElement("div", { className: "auth-loading" },
                React.createElement("div", { className: "spinner" }),
                " Checking your session\u2026") : unavailable ? React.createElement("button", { className: "button button-primary full-button", onClick: onRetry },
                React.createElement(Icon, { name: "refresh" }),
                " Retry connection") :
                React.createElement("form", { onSubmit: onSubmit, className: "auth-form" },
                    React.createElement("label", { htmlFor: "owner-username" }, "Username"),
                    React.createElement("input", { id: "owner-username", autoComplete: "username", value: username, onChange: e => onUsername(e.target.value), minLength: 3, maxLength: 30, required: true, placeholder: "farhan" }),
                    React.createElement("label", { htmlFor: "owner-password" }, setup ? 'Create password' : 'Password'),
                    React.createElement("input", { id: "owner-password", type: "password", autoComplete: setup ? 'new-password' : 'current-password', minLength: setup ? 12 : 1, maxLength: 128, required: true, value: password, onChange: e => onPassword(e.target.value), placeholder: setup ? 'At least 12 characters' : 'Enter your password' }),
                    setup ? React.createElement("div", { className: "auth-confirm-group" },
                        React.createElement("label", { htmlFor: "owner-confirm" }, "Confirm password"),
                        React.createElement("input", { id: "owner-confirm", type: "password", autoComplete: "new-password", minLength: 12, required: true, value: confirm, onChange: e => onConfirm(e.target.value), placeholder: "Repeat your new password" })) : null,
                    React.createElement("button", { className: "button button-primary full-button auth-submit", type: "submit", disabled: busy },
                        busy ? 'Please wait…' : setup ? 'Create secure workspace' : 'Sign in securely',
                        React.createElement(Icon, { name: "arrow", size: 17 }))),
            React.createElement("div", { className: "auth-trust" },
                React.createElement(Icon, { name: "lock", size: 17 }),
                " No shared default password. Data is stored on your device.")),
        React.createElement("div", { className: "auth-foot" }, "\u00A9 2026 SentinelScan \u2014 Built by Farhan Ali \u00B7 Local-first private workspace"));
}
class App extends React.Component {
    constructor(props) { super(props); this.state = { active: 'overview', scans: [], selectedId: null, busy: false, loading: true, error: '', notice: '', target: '', filter: '', settingsOpen: false, menuOpen: false, apiBase: localStorage.getItem(API_STORAGE_KEY) || DEFAULT_API, baseInput: localStorage.getItem(API_STORAGE_KEY) || DEFAULT_API, liveEnabled: false, authState: 'checking', authError: '', authUsername: 'farhan', authPassword: '', authConfirm: '', authBusy: false, token: sessionStorage.getItem(TOKEN_KEY) || '', owner: '', events: [], compareA: '', compareB: '', currentPassword: '', newPassword: '', confirmNewPassword: '' }; this.runDemo = this.runDemo.bind(this); this.runLive = this.runLive.bind(this); this.load = this.load.bind(this); this.select = this.select.bind(this); }
    componentDidMount() { this.bootstrap(); }
    get api() { return this.state.apiBase.replace(/\/+$/, ''); }
    async request(path, options = {}) {
        const token = this.state.token;
        const headers = { ...(options.headers || {}) };
        if (token)
            headers.Authorization = 'Bearer ' + token;
        const res = await fetch(this.api + path, { ...options, headers, cache: 'no-store' });
        const data = res.status === 204 ? {} : await res.json().catch(() => ({}));
        if (!res.ok) {
            if (res.status === 401 && this.state.authState === 'ready')
                this.expireSession();
            throw new Error(typeof data.detail === 'string' ? data.detail : 'Request failed (' + res.status + ')');
        }
        return data;
    }
    expireSession() { sessionStorage.removeItem(TOKEN_KEY); this.setState({ authState: 'login', token: '', authPassword: '', authError: 'Session expired. Sign in again.', scans: [], events: [] }); }
    async bootstrap() {
        this.setState({ authState: 'checking', authError: '' });
        try {
            const status = await this.request('/api/auth/status');
            if (!status.configured) {
                sessionStorage.removeItem(TOKEN_KEY);
                return this.setState({ authState: 'setup', token: '', authError: '' });
            }
            if (this.state.token) {
                try {
                    const me = await this.request('/api/auth/me');
                    this.setState({ authState: 'ready', owner: me.username, authUsername: me.username }, () => this.load());
                    return;
                }
                catch (_) {
                    sessionStorage.removeItem(TOKEN_KEY);
                }
            }
            this.setState({ authState: 'login', token: '', authPassword: '', authError: '' });
        }
        catch (err) {
            this.setState({ authState: 'offline', authError: 'Cannot connect to the API. ' + err.message });
        }
    }
    async submitAuth(e) {
        e.preventDefault();
        if (this.state.authBusy)
            return;
        if (this.state.authState === 'setup' && this.state.authPassword !== this.state.authConfirm)
            return this.setState({ authError: 'Passwords do not match.' });
        this.setState({ authBusy: true, authError: '' });
        try {
            const setup = this.state.authState === 'setup';
            const result = await this.request(setup ? '/api/auth/setup' : '/api/auth/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username: this.state.authUsername.trim(), password: this.state.authPassword }) });
            sessionStorage.setItem(TOKEN_KEY, result.token);
            this.setState({ authBusy: false, authState: 'ready', token: result.token, owner: result.username, authPassword: '', authConfirm: '' }, () => this.load());
        }
        catch (err) {
            this.setState({ authBusy: false, authError: err.message });
        }
    }
    async logout() { try {
        await this.request('/api/auth/logout', { method: 'POST' });
    }
    catch (_) { } sessionStorage.removeItem(TOKEN_KEY); this.setState({ authState: 'login', token: '', authPassword: '', scans: [], events: [], authError: '' }); }
    async changePassword(e) {
        e.preventDefault();
        if (this.state.newPassword !== this.state.confirmNewPassword)
            return this.setState({ error: 'New passwords do not match.' });
        try {
            await this.request('/api/auth/password', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ current_password: this.state.currentPassword, new_password: this.state.newPassword }) });
            this.setState({ settingsOpen: false, currentPassword: '', newPassword: '', confirmNewPassword: '' }, () => this.logout());
        }
        catch (err) {
            this.setState({ error: err.message, settingsOpen: false });
        }
    }
    async downloadFile(path, name) {
        try {
            const res = await fetch(this.api + path, { headers: { 'Authorization': 'Bearer ' + this.state.token }, cache: 'no-store' });
            if (!res.ok) {
                if (res.status === 401)
                    this.expireSession();
                const data = await res.json().catch(() => ({}));
                throw new Error(data.detail || 'Download failed');
            }
            const url = URL.createObjectURL(await res.blob());
            const a = document.createElement('a');
            a.href = url;
            a.download = name;
            document.body.appendChild(a);
            a.click();
            a.remove();
            setTimeout(() => URL.revokeObjectURL(url), 1000);
        }
        catch (err) {
            this.setState({ error: err.message });
        }
    }
    async deleteScan(id) {
        if (!window.confirm('Permanently delete assessment #' + id + '? This cannot be undone.'))
            return;
        try {
            await this.request('/api/scans/' + id, { method: 'DELETE' });
            this.setState(s => { var _a; const scans = s.scans.filter(x => x.id !== id); return { scans, selectedId: scans.some(x => x.id === s.selectedId) ? s.selectedId : ((_a = scans[0]) === null || _a === void 0 ? void 0 : _a.id) || null, notice: 'Assessment deleted.' }; });
        }
        catch (err) {
            this.setState({ error: err.message });
        }
    }
    async loadActivity() { try {
        const events = await this.request('/api/audit');
        this.setState({ events });
    }
    catch (err) {
        this.setState({ error: err.message });
    } }
    async load() { this.setState({ loading: true, error: '' }); try {
        const health = await this.request('/api/health');
        let scans = await this.request('/api/scans');
        if (scans.length === 0) {
            await this.request('/api/scans/demo', { method: 'POST' });
            scans = await this.request('/api/scans');
        }
        this.setState((prev) => { var _a; return ({ scans, selectedId: scans.some(s => s.id === prev.selectedId) ? prev.selectedId : ((_a = scans[0]) === null || _a === void 0 ? void 0 : _a.id) || null, loading: false, liveEnabled: health.live_scans_enabled }); });
    }
    catch (err) {
        this.setState({ loading: false, error: 'Cannot reach the SentinelScan API. Start the Python backend, then retry. ' + err.message });
    } }
    async runDemo() { if (this.state.busy)
        return; this.setState({ busy: true, error: '', notice: '' }); try {
        const scan = await this.request('/api/scans/demo', { method: 'POST' });
        this.setState(s => ({ busy: false, scans: [scan, ...s.scans], selectedId: scan.id, notice: 'Offline demo scan created successfully.', active: 'overview' }));
    }
    catch (err) {
        this.setState({ busy: false, error: err.message });
    } }
    async runLive(e) { e.preventDefault(); if (this.state.busy)
        return; const target = this.state.target.trim(); if (!target)
        return this.setState({ error: 'Enter a website URL first.' }); this.setState({ busy: true, error: '', notice: '' }); try {
        const scan = await this.request('/api/scans', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ target }) });
        this.setState(s => ({ busy: false, scans: [scan, ...s.scans], selectedId: scan.id, notice: 'Authorized scan finished and saved.', target: '', active: 'overview' }));
    }
    catch (err) {
        this.setState({ busy: false, error: err.message });
    } }
    select(id) { this.setState({ selectedId: id, active: 'findings', filter: '', menuOpen: false }); window.scrollTo({ top: 0, behavior: 'smooth' }); }
    nav(id) { this.setState({ active: id, menuOpen: false, filter: '' }); if (id === 'activity')
        this.loadActivity(); window.scrollTo({ top: 0, behavior: 'smooth' }); }
    saveSettings(e) { e.preventDefault(); let candidate = this.state.baseInput.trim().replace(/\/+$/, ''); try {
        let parsed = new URL(candidate);
        if (!['http:', 'https:'].includes(parsed.protocol))
            throw new Error();
        if (parsed.username || parsed.password)
            throw new Error();
        localStorage.setItem(API_STORAGE_KEY, candidate);
        sessionStorage.removeItem(TOKEN_KEY);
        this.setState({ apiBase: candidate, settingsOpen: false, scans: [], selectedId: null, token: '', authState: 'checking' }, () => this.bootstrap());
    }
    catch (_) {
        this.setState({ error: 'Enter a valid HTTP(S) API origin.' });
    } }
    render() {
        var _a;
        const s = this.state, selected = s.scans.find(x => x.id === s.selectedId) || s.scans[0] || null;
        const findings = (selected === null || selected === void 0 ? void 0 : selected.findings) || [];
        const failed = findings.filter(x => x.severity !== 'pass');
        const high = failed.filter(x => x.severity === 'high' || x.severity === 'critical').length;
        const passed = findings.filter(x => x.severity === 'pass').length;
        const avg = s.scans.length ? Math.round(s.scans.reduce((sum, x) => sum + x.score, 0) / s.scans.length) : 0;
        if (s.authState !== 'ready')
            return React.createElement(AuthScreen, { mode: s.authState, error: s.authError, username: s.authUsername, password: s.authPassword, confirm: s.authConfirm, busy: s.authBusy, onUsername: v => this.setState({ authUsername: v }), onPassword: v => this.setState({ authPassword: v }), onConfirm: v => this.setState({ authConfirm: v }), onSubmit: e => this.submitAuth(e), onRetry: () => this.bootstrap() });
        const compareOne = s.scans.find(x => String(x.id) === String(s.compareA)) || s.scans[1] || s.scans[0];
        const compareTwo = s.scans.find(x => String(x.id) === String(s.compareB)) || s.scans[0];
        return React.createElement("div", { className: "app-shell" },
            React.createElement("aside", { className: 'sidebar ' + (s.menuOpen ? 'sidebar-open' : '') },
                React.createElement(Brand, null),
                React.createElement("div", { className: "side-caption" }, "WORKSPACE"),
                React.createElement("nav", { className: "main-nav" }, NAV.map(n => React.createElement("button", { key: n.id, className: 'nav-item ' + (s.active === n.id ? 'active' : ''), onClick: () => this.nav(n.id) },
                    React.createElement(Icon, { name: n.icon }),
                    n.text,
                    n.id === 'findings' && high > 0 ? React.createElement("span", { className: "nav-count" }, high) : null))),
                React.createElement("div", { className: "side-caption tools-caption" }, "PREFERENCES"),
                React.createElement("button", { className: "nav-item", onClick: () => this.setState({ settingsOpen: true, menuOpen: false }) },
                    React.createElement(Icon, { name: "settings" }),
                    "Settings"),
                React.createElement("div", { className: "sidebar-spacer" }),
                React.createElement("div", { className: "sidebar-promo" },
                    React.createElement("div", { className: "promo-spark" },
                        React.createElement(Icon, { name: "lock" })),
                    React.createElement("strong", null, "Secure by design."),
                    React.createElement("p", null, "Passive checks. Explicit allowlist. Your data stays local."),
                    React.createElement("div", { className: "promo-foot" },
                        React.createElement("span", { className: "pulse-dot" }),
                        "LOCAL MODE")),
                React.createElement("div", { className: "sidebar-footer" },
                    React.createElement("div", { className: "avatar" }, (s.owner || 'FA').slice(0, 2).toUpperCase()),
                    React.createElement("div", null,
                        React.createElement("strong", null, s.owner),
                        React.createElement("span", null, "Secure owner workspace")),
                    React.createElement("button", { className: "icon-button", "aria-label": "Sign out", title: "Sign out", onClick: () => this.logout() },
                        React.createElement(Icon, { name: "logout", size: 17 })))),
            React.createElement("div", { className: "main-area" },
                React.createElement("header", { className: "topbar" },
                    React.createElement("div", { className: "crumb" },
                        React.createElement("button", { className: "menu-button", "aria-label": "Open menu", onClick: () => this.setState({ menuOpen: !s.menuOpen }) },
                            React.createElement(Icon, { name: "menu" })),
                        React.createElement("span", null, "Workspace"),
                        React.createElement("span", { className: "crumb-div" }, "/"),
                        React.createElement("b", null, ((_a = NAV.find(n => n.id === s.active)) === null || _a === void 0 ? void 0 : _a.text) || 'Overview')),
                    React.createElement("div", { className: "topbar-right" },
                        React.createElement("span", { className: "connection" },
                            React.createElement("span", { className: 'connection-dot ' + (s.error ? 'off' : '') }),
                            s.error ? 'Disconnected' : 'Local dashboard'),
                        React.createElement("button", { className: "top-icon", "aria-label": "Refresh data", title: "Refresh", onClick: this.load },
                            React.createElement(Icon, { name: "refresh" })),
                        React.createElement("div", { className: "top-avatar" }, (s.owner || 'FA').slice(0, 2).toUpperCase()))),
                React.createElement("main", { className: "page-body" },
                    React.createElement("div", { className: "page-header" },
                        React.createElement("div", null,
                            React.createElement("div", { className: "eyebrow flex-eyebrow" },
                                React.createElement("span", { className: "eyebrow-line" }),
                                " THE SECURITY CONTROL CENTER"),
                            React.createElement("h1", null,
                                s.active === 'overview' ? 'Security overview' : s.active === 'history' ? 'Scan history' : s.active === 'findings' ? 'Security findings' : s.active === 'compare' ? 'Compare assessments' : s.active === 'activity' ? 'Workspace activity' : 'Security reports',
                                React.createElement("span", { className: "heading-period" }, ".")),
                            React.createElement("p", null, s.active === 'overview' ? 'Monitor your web security posture, all in one place.' : s.active === 'history' ? 'Explore your assessment history and track changes over time.' : s.active === 'findings' ? 'Understand configuration issues and how to improve them.' : s.active === 'compare' ? 'Track improvements across two saved security assessments.' : s.active === 'activity' ? 'Review the actions recorded in your private workspace.' : 'Export comprehensive reports for your saved assessments.')),
                        React.createElement("div", { className: "header-actions" },
                            React.createElement("button", { className: "button button-outline", onClick: this.load, disabled: s.loading },
                                React.createElement(Icon, { name: "refresh", size: 16 }),
                                " Refresh"),
                            React.createElement("button", { className: "button button-primary", onClick: this.runDemo, disabled: s.busy },
                                React.createElement(Icon, { name: "bolt", size: 16 }),
                                s.busy ? 'Scanning…' : 'Run demo scan'))),
                    s.error ? React.createElement("div", { className: "message error-message" },
                        React.createElement(Icon, { name: "alert", size: 19 }),
                        React.createElement("div", null,
                            s.error,
                            React.createElement("button", { onClick: this.load }, "Retry connection")),
                        React.createElement("button", { "aria-label": "Dismiss", onClick: () => this.setState({ error: '' }) },
                            React.createElement(Icon, { name: "close", size: 15 }))) : null,
                    s.notice ? React.createElement("div", { className: "message success-message" },
                        React.createElement(Icon, { name: "check", size: 17 }),
                        React.createElement("span", null, s.notice),
                        React.createElement("button", { "aria-label": "Dismiss", onClick: () => this.setState({ notice: '' }) },
                            React.createElement(Icon, { name: "close", size: 15 }))) : null,
                    s.loading ? React.createElement("div", { className: "loading-block" },
                        React.createElement("div", { className: "spinner" }),
                        React.createElement("h3", null, "Connecting to SentinelScan"),
                        React.createElement("p", null, "Loading your assessments\u2026")) : React.createElement("g", null,
                        s.active === 'overview' ? React.createElement("g", null,
                            React.createElement("section", { className: "hero-card" },
                                React.createElement(DotGrid, null),
                                React.createElement("div", { className: "hero-copy" },
                                    React.createElement("div", { className: "hero-tag" },
                                        React.createElement("span", { className: "pulse-dot" }),
                                        " ",
                                        (selected === null || selected === void 0 ? void 0 : selected.demo) ? 'OFFLINE DEMO PREVIEW' : 'LIVE SECURITY POSTURE'),
                                    React.createElement("h2", null,
                                        "Your security,",
                                        React.createElement("br", null),
                                        React.createElement("em", null, "under control.")),
                                    React.createElement("p", null, "Know where you stand. Detect misconfigurations, understand risk and make informed improvements."),
                                    React.createElement("div", { className: "hero-footer" },
                                        React.createElement("span", null,
                                            React.createElement(Icon, { name: "shield", size: 16 }),
                                            " Passive assessment"),
                                        React.createElement("span", null,
                                            React.createElement(Icon, { name: "lock", size: 16 }),
                                            " Permission-based"))),
                                React.createElement("div", { className: "hero-ring" },
                                    React.createElement("div", { className: "ring-glow" }),
                                    React.createElement(ScoreRing, { score: (selected === null || selected === void 0 ? void 0 : selected.score) || 0 }),
                                    React.createElement("div", { className: "hero-ring-caption" }, selected ? 'LATEST ASSESSMENT' : 'AWAITING FIRST SCAN'))),
                            React.createElement("form", { className: "scan-bar", onSubmit: this.runLive },
                                React.createElement("div", { className: "scan-icon" },
                                    React.createElement(Icon, { name: "globe", size: 21 })),
                                React.createElement("div", { className: "scan-input-area" },
                                    React.createElement("label", { htmlFor: "target-url" }, "START NEW ASSESSMENT"),
                                    React.createElement("input", { id: "target-url", type: "url", placeholder: "https://your-authorized-website.com", value: s.target, onChange: e => this.setState({ target: e.target.value }), required: true })),
                                React.createElement("button", { className: "button button-primary scan-button", disabled: s.busy || !s.liveEnabled, type: "submit" },
                                    React.createElement(Icon, { name: s.busy ? 'refresh' : 'arrow', size: 17 }),
                                    s.busy ? 'Scanning…' : 'Scan website')),
                            React.createElement("div", { className: "scan-hint" },
                                React.createElement(Icon, { name: "info", size: 14 }),
                                s.liveEnabled ? 'Only hosts in your configured ALLOWED_TARGET_HOSTS can be scanned.' : 'Live scans are disabled until ALLOWED_TARGET_HOSTS is configured in the backend .env file.'),
                            React.createElement("div", { className: "metrics" },
                                React.createElement("div", { className: "metric-card" },
                                    React.createElement("div", { className: "metric-head" },
                                        React.createElement("span", null, "Overall score"),
                                        React.createElement("div", { className: "metric-icon aqua" },
                                            React.createElement(Icon, { name: "shield" }))),
                                    React.createElement("div", { className: "metric-value" },
                                        selected ? selected.score : '—',
                                        React.createElement("small", null, "/100")),
                                    React.createElement("div", { className: "metric-caption" },
                                        React.createElement("span", { className: 'metric-indicator ' + scoreClass((selected === null || selected === void 0 ? void 0 : selected.score) || 0) }, selected ? (selected.score >= 80 ? 'Healthy' : selected.score >= 55 ? 'Needs attention' : 'Action recommended') : 'Not yet scanned'))),
                                React.createElement("div", { className: "metric-card" },
                                    React.createElement("div", { className: "metric-head" },
                                        React.createElement("span", null, "Total scans"),
                                        React.createElement("div", { className: "metric-icon violet" },
                                            React.createElement(Icon, { name: "activity" }))),
                                    React.createElement("div", { className: "metric-value" }, s.scans.length.toString().padStart(2, '0')),
                                    React.createElement("div", { className: "metric-caption" }, "Saved assessments")),
                                React.createElement("div", { className: "metric-card" },
                                    React.createElement("div", { className: "metric-head" },
                                        React.createElement("span", null, "Open findings"),
                                        React.createElement("div", { className: "metric-icon amber" },
                                            React.createElement(Icon, { name: "alert" }))),
                                    React.createElement("div", { className: "metric-value" }, String(failed.length).padStart(2, '0')),
                                    React.createElement("div", { className: "metric-caption" },
                                        React.createElement("span", { className: "critical-caption" },
                                            high,
                                            " high priority"),
                                        " on selected scan")),
                                React.createElement("div", { className: "metric-card" },
                                    React.createElement("div", { className: "metric-head" },
                                        React.createElement("span", null, "Passed checks"),
                                        React.createElement("div", { className: "metric-icon green" },
                                            React.createElement(Icon, { name: "check" }))),
                                    React.createElement("div", { className: "metric-value" }, String(passed).padStart(2, '0')),
                                    React.createElement("div", { className: "metric-caption" },
                                        "of ",
                                        findings.length,
                                        " checks verified"))),
                            React.createElement("div", { className: "chart-grid" },
                                React.createElement("section", { className: "panel trend-panel" },
                                    React.createElement(SectionHead, { eyebrow: "PERFORMANCE", title: "Security score trend", right: React.createElement("span", { className: "panel-flag" },
                                            "Last ",
                                            Math.min(8, s.scans.length),
                                            " scans") }),
                                    React.createElement(TrendChart, { scans: s.scans })),
                                React.createElement("section", { className: "panel" },
                                    React.createElement(SectionHead, { eyebrow: "RISK BREAKDOWN", title: "Findings by category", right: React.createElement("div", { className: "soft-round" },
                                            React.createElement(Icon, { name: "activity", size: 17 })) }),
                                    React.createElement(Distribution, { findings: findings }),
                                    React.createElement("div", { className: "distribution-footer" },
                                        React.createElement("span", { className: "legend-dot" }),
                                        " Based on selected assessment"))),
                            React.createElement("div", { className: "content-grid" },
                                React.createElement("section", { className: "panel recent-panel" },
                                    React.createElement(SectionHead, { eyebrow: "ACTIVITY LOG", title: "Recent assessments", right: React.createElement("button", { className: "text-link", onClick: () => this.nav('history') },
                                            "View all ",
                                            React.createElement(Icon, { name: "arrow", size: 15 })) }),
                                    React.createElement(HistoryTable, { scans: s.scans.slice(0, 5), onSelect: this.select, selectedId: s.selectedId, onDelete: id => this.deleteScan(id) })),
                                React.createElement("section", { className: "panel issue-panel" },
                                    React.createElement(SectionHead, { eyebrow: "ACTION ITEMS", title: "Latest findings", right: React.createElement("button", { className: "text-link", onClick: () => this.nav('findings') },
                                            "View all ",
                                            React.createElement(Icon, { name: "arrow", size: 15 })) }),
                                    React.createElement(Findings, { scan: selected, limit: 4 })))) : null,
                        s.active === 'history' ? React.createElement("section", { className: "panel large-panel" },
                            React.createElement(SectionHead, { eyebrow: "ASSESSMENTS", title: "All completed scans", right: React.createElement("span", { className: "panel-flag" },
                                    s.scans.length,
                                    " total") }),
                            React.createElement(HistoryTable, { scans: s.scans, onSelect: this.select, selectedId: s.selectedId, onDelete: id => this.deleteScan(id) })) : null,
                        s.active === 'findings' ? React.createElement("div", { className: "detail-grid" },
                            React.createElement("div", null,
                                React.createElement("section", { className: "panel detail-overview" },
                                    React.createElement("div", { className: "detail-score" },
                                        React.createElement(ScoreRing, { score: (selected === null || selected === void 0 ? void 0 : selected.score) || 0, size: 164 })),
                                    React.createElement("div", null,
                                        React.createElement("div", { className: "eyebrow" }, "SELECTED ASSESSMENT"),
                                        React.createElement("h2", null, selected ? displayHost(selected.target) : 'No scan selected'),
                                        React.createElement("p", null, selected ? formatDate(selected.scanned_at) : 'Run a scan to view details.'),
                                        selected ? React.createElement("span", { className: selected.demo ? 'demo-label' : 'live-label' }, selected.demo ? '● Offline demo' : '● Authorized live scan') : null)),
                                React.createElement("section", { className: "panel findings-section" },
                                    React.createElement(SectionHead, { eyebrow: "DETAILED RESULTS", title: "Configuration findings", right: React.createElement("span", { className: "panel-flag" },
                                            findings.length,
                                            " checks") }),
                                    React.createElement("div", { className: "search-box" },
                                        React.createElement(Icon, { name: "search", size: 17 }),
                                        React.createElement("input", { placeholder: "Search findings\u2026", value: s.filter, onChange: e => this.setState({ filter: e.target.value }) })),
                                    React.createElement(Findings, { scan: selected, query: s.filter }))),
                            React.createElement("div", null,
                                React.createElement("section", { className: "panel action-panel" },
                                    React.createElement("div", { className: "action-icon" },
                                        React.createElement(Icon, { name: "shield", size: 25 })),
                                    React.createElement("h3", null, "Understanding the score"),
                                    React.createElement("p", null, "SentinelScan checks passive HTTP and TLS configuration indicators. Scores are not guarantees of site security or a penetration test."),
                                    React.createElement("div", { className: "action-stat" },
                                        React.createElement("span", null, "High priority"),
                                        React.createElement("b", null, high)),
                                    React.createElement("div", { className: "action-stat" },
                                        React.createElement("span", null, "Passed"),
                                        React.createElement("b", null, passed)),
                                    selected ? React.createElement("button", { className: "button button-primary full-button", onClick: () => this.downloadFile('/api/scans/' + selected.id + '/report.pdf', 'sentinelscan-report-' + selected.id + '.pdf') },
                                        React.createElement(Icon, { name: "down", size: 16 }),
                                        " Download PDF") : null),
                                React.createElement("section", { className: "panel selector-panel" },
                                    React.createElement("div", { className: "eyebrow" }, "SWITCH ASSESSMENT"),
                                    s.scans.slice(0, 7).map(scan => React.createElement("button", { className: 'select-scan ' + ((selected === null || selected === void 0 ? void 0 : selected.id) === scan.id ? 'chosen' : ''), key: scan.id, onClick: () => this.setState({ selectedId: scan.id }) },
                                        React.createElement("span", null,
                                            React.createElement("strong", null, displayHost(scan.target)),
                                            React.createElement("small", null,
                                                "#",
                                                scan.id,
                                                " \u00B7 ",
                                                scan.score,
                                                "/100")),
                                        React.createElement(Icon, { name: "arrow", size: 16 })))))) : null,
                        s.active === 'compare' ? React.createElement("section", { className: "panel large-panel" },
                            React.createElement(SectionHead, { eyebrow: "CHANGE ANALYSIS", title: "Compare two assessments", right: React.createElement("span", { className: "panel-flag" }, "Stored results \u00B7 No new scans") }),
                            s.scans.length < 2 ? React.createElement("div", { className: "quiet-empty" }, "Create at least two scans to compare their scores and findings.") : React.createElement("div", null,
                                React.createElement("div", { className: "compare-selectors" },
                                    React.createElement("div", null,
                                        React.createElement("label", { htmlFor: "compare-old" }, "Baseline scan"),
                                        React.createElement("select", { id: "compare-old", value: compareOne === null || compareOne === void 0 ? void 0 : compareOne.id, onChange: e => this.setState({ compareA: e.target.value }) }, s.scans.map(x => React.createElement("option", { key: x.id, value: x.id },
                                            "#",
                                            x.id,
                                            " \u2014 ",
                                            displayHost(x.target),
                                            " (",
                                            x.score,
                                            "/100)")))),
                                    React.createElement("div", null,
                                        React.createElement("label", { htmlFor: "compare-new" }, "Latest scan"),
                                        React.createElement("select", { id: "compare-new", value: compareTwo === null || compareTwo === void 0 ? void 0 : compareTwo.id, onChange: e => this.setState({ compareB: e.target.value }) }, s.scans.map(x => React.createElement("option", { key: x.id, value: x.id },
                                            "#",
                                            x.id,
                                            " \u2014 ",
                                            displayHost(x.target),
                                            " (",
                                            x.score,
                                            "/100)"))))),
                                React.createElement("div", { className: "compare-cards" },
                                    React.createElement("div", { className: "compare-score" },
                                        React.createElement("div", { className: "eyebrow" }, "BASELINE"),
                                        React.createElement("strong", null,
                                            compareOne.score,
                                            React.createElement("small", null, " / 100")),
                                        React.createElement("span", null, displayHost(compareOne.target))),
                                    React.createElement("div", { className: "compare-score" },
                                        React.createElement("div", { className: "eyebrow" }, "LATEST"),
                                        React.createElement("strong", null,
                                            compareTwo.score,
                                            React.createElement("small", null, " / 100")),
                                        React.createElement("span", null, displayHost(compareTwo.target))),
                                    React.createElement("div", { className: "compare-score delta-score" },
                                        React.createElement("div", { className: "eyebrow" }, "SCORE DELTA"),
                                        React.createElement("strong", null,
                                            compareTwo.score - compareOne.score > 0 ? '+' : '',
                                            compareTwo.score - compareOne.score),
                                        React.createElement("span", null, compareTwo.score > compareOne.score ? 'Improvement' : compareTwo.score < compareOne.score ? 'Needs attention' : 'No score change'))),
                                React.createElement("p", { className: "intro-text" }, "This compares stored scores only. Use Findings to compare individual security checks. Each score is a limited configuration assessment, not a vulnerability guarantee."))) : null,
                        s.active === 'activity' ? React.createElement("section", { className: "panel large-panel" },
                            React.createElement(SectionHead, { eyebrow: "AUDIT TRAIL", title: "Recent workspace actions", right: React.createElement("button", { className: "button button-outline", onClick: () => this.loadActivity() },
                                    React.createElement(Icon, { name: "refresh", size: 16 }),
                                    " Refresh") }),
                            s.events.length ? React.createElement("div", { className: "audit-list" }, s.events.map(e => React.createElement("div", { className: "audit-row", key: e.id },
                                React.createElement("div", { className: "audit-icon" },
                                    React.createElement(Icon, { name: "activity", size: 17 })),
                                React.createElement("div", null,
                                    React.createElement("strong", null, e.action.replace(/_/g, ' ')),
                                    React.createElement("small", null, e.details)),
                                React.createElement("span", null, formatDate(new Date(e.created_at * 1000).toISOString()))))) : React.createElement("div", { className: "quiet-empty" }, "No recent activity found.")) : null,
                        s.active === 'reports' ? React.createElement("section", { className: "panel large-panel" },
                            React.createElement(SectionHead, { eyebrow: "EXPORT CENTER", title: "Saved security reports", right: React.createElement("button", { className: "button button-outline", onClick: () => this.downloadFile('/api/reports/scans.csv', 'sentinelscan-history.csv') },
                                    React.createElement(Icon, { name: "down", size: 16 }),
                                    " Export CSV") }),
                            React.createElement("p", { className: "intro-text" }, "Download a professionally formatted, offline-ready assessment of any saved scan. Reports include scores, evidence, and recommended fixes."),
                            React.createElement("div", { className: "report-list" }, s.scans.map(scan => React.createElement("div", { className: "report-row", key: scan.id },
                                React.createElement("div", { className: "report-file" },
                                    React.createElement(Icon, { name: "file", size: 23 })),
                                React.createElement("div", { className: "report-data" },
                                    React.createElement("strong", null, displayHost(scan.target)),
                                    React.createElement("span", null,
                                        "Assessment #",
                                        scan.id,
                                        " \u00B7 ",
                                        formatDate(scan.scanned_at),
                                        " \u00B7 ",
                                        scan.findings.length,
                                        " checks")),
                                React.createElement("span", { className: 'score-pill ' + scoreClass(scan.score) },
                                    scan.score,
                                    "/100"),
                                React.createElement("button", { className: "button button-outline report-download", onClick: () => this.downloadFile('/api/scans/' + scan.id + '/report.pdf', 'sentinelscan-report-' + scan.id + '.pdf') },
                                    React.createElement(Icon, { name: "down", size: 16 }),
                                    " PDF"))))) : null),
                    React.createElement("footer", { className: "footer" },
                        React.createElement("span", null,
                            "\u00A9 2026 SentinelScan \u00B7 Built by ",
                            React.createElement("b", null, "Farhan Ali")),
                        React.createElement("span", null,
                            React.createElement("span", { className: "footer-dot" }),
                            " Private by default \u00B7 Version 2.0.0")))),
            s.settingsOpen ? React.createElement("div", { className: "modal-backdrop", onClick: () => this.setState({ settingsOpen: false }) },
                React.createElement("div", { className: "modal", onClick: e => e.stopPropagation() },
                    React.createElement("div", { className: "modal-heading" },
                        React.createElement("h2", null, "Workspace settings"),
                        React.createElement("button", { className: "icon-button", "aria-label": "Close settings", onClick: () => this.setState({ settingsOpen: false }) },
                            React.createElement(Icon, { name: "close" }))),
                    React.createElement("p", null,
                        "Workspace owner: ",
                        React.createElement("b", null, s.owner),
                        ". The API address must be trusted: changing it signs you out and your next login is sent to that server. Live targets are configured in the backend .env file."),
                    React.createElement("form", { onSubmit: e => this.saveSettings(e) },
                        React.createElement("label", { htmlFor: "api-base" }, "API origin"),
                        React.createElement("input", { id: "api-base", value: s.baseInput, onChange: e => this.setState({ baseInput: e.target.value }), placeholder: "http://localhost:8000" }),
                        React.createElement("button", { type: "submit", className: "button button-outline full-button" }, "Save API address & sign out")),
                    React.createElement("div", { className: "settings-divider" }),
                    React.createElement("h3", null, "Change owner password"),
                    React.createElement("p", null, "Changing the password signs out all existing sessions."),
                    React.createElement("form", { onSubmit: e => this.changePassword(e) },
                        React.createElement("label", { htmlFor: "current-password" }, "Current password"),
                        React.createElement("input", { id: "current-password", type: "password", autoComplete: "current-password", value: s.currentPassword, onChange: e => this.setState({ currentPassword: e.target.value }), required: true }),
                        React.createElement("label", { htmlFor: "new-password" }, "New password \u00B7 12+ characters"),
                        React.createElement("input", { id: "new-password", type: "password", minLength: 12, maxLength: 128, autoComplete: "new-password", value: s.newPassword, onChange: e => this.setState({ newPassword: e.target.value }), required: true }),
                        React.createElement("label", { htmlFor: "new-password-confirm" }, "Confirm new password"),
                        React.createElement("input", { id: "new-password-confirm", type: "password", minLength: 12, autoComplete: "new-password", value: s.confirmNewPassword, onChange: e => this.setState({ confirmNewPassword: e.target.value }), required: true }),
                        React.createElement("button", { type: "submit", className: "button button-primary full-button" }, "Update password")))) : null);
    }
}
ReactDOM.render(React.createElement(App, null), document.getElementById('root'));
