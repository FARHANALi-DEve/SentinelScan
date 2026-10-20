"""Read-only security posture indicators for explicitly authorized web hosts."""
from datetime import datetime, timezone
import http.client
import socket
import ssl
from urllib.parse import urljoin
from .policy import PolicyError, TargetPolicy, ValidatedTarget

MAX_REDIRECTS = 3
WEIGHTS = {'critical':30,'high':20,'medium':10,'low':5,'info':0,'pass':0}


def finding(check_id, title, severity, category, description, evidence, recommendation):
    return dict(check_id=check_id, title=title, severity=severity, category=category,
                description=description, evidence=str(evidence)[:280], recommendation=recommendation)


def score_findings(findings):
    return max(0, 100 - sum(WEIGHTS.get(f['severity'],0) for f in findings))


def evaluate_headers(headers, scheme, tls_info=None):
    """Generate bounded findings; never emit raw cookie values or tokens."""
    h = {str(k).lower():str(v) for k,v in headers.items()}
    result=[]
    specs=[
        ('csp','Content Security Policy','high','Browser protection','Content Security Policy limits injected scripts.', 'content-security-policy','Set a restrictive Content-Security-Policy appropriate for your site.'),
        ('hsts','HTTP Strict Transport Security','medium','Transport','HSTS tells browsers to prefer HTTPS.', 'strict-transport-security','Add Strict-Transport-Security with an appropriate max-age after HTTPS is stable.'),
        ('nosniff','MIME sniffing protection','medium','Browser protection','X-Content-Type-Options prevents MIME type sniffing.','x-content-type-options','Set X-Content-Type-Options: nosniff.'),
        ('referrer','Referrer Policy','low','Privacy','Referrer-Policy controls URL metadata sent to other sites.','referrer-policy','Set Referrer-Policy: strict-origin-when-cross-origin or stricter.'),
        ('permissions','Permissions Policy','low','Privacy','Permissions-Policy restricts browser features.','permissions-policy','Declare a Permissions-Policy that disables unused browser features.'),
    ]
    for key, title, severity, category, desc, header, fix in specs:
        present=bool(h.get(header))
        if key=='hsts' and scheme!='https':
            continue
        if key=='nosniff':
            present=h.get(header,'').strip().lower()=='nosniff'
        if key=='hsts':
            present=present and 'max-age=' in h.get(header,'').lower()
        result.append(finding(key,title,'pass' if present else severity,category,desc,'Configured' if present else f'{header} absent or invalid',fix))
    framed=bool(h.get('x-frame-options')) or 'frame-ancestors' in h.get('content-security-policy','')
    result.append(finding('frame','Clickjacking protection','pass' if framed else 'medium','Browser protection','Prevent unauthorized embedding in frames.','Protected' if framed else 'Missing X-Frame-Options / CSP frame-ancestors','Add CSP frame-ancestors or X-Frame-Options: DENY.'))
    if scheme=='http':
        result.append(finding('transport','Unencrypted transport','high','Transport','HTTP can expose traffic to interception.','Target uses HTTP','Redirect to HTTPS and update all links.'))
    else:
        if tls_info is None or not tls_info.get('valid'):
            result.append(finding('certificate','TLS certificate verification','high','TLS','Certificate identity and trust must validate.','TLS details unavailable','Use a trusted valid certificate for the configured hostname.'))
        else:
            days=tls_info.get('days_remaining')
            if isinstance(days,(int,float)):
                result.append(finding('certificate','TLS certificate expiration','medium' if days < 14 else 'pass','TLS','Certificates need renewal before expiration.',f'{int(days)} days remaining','Renew the TLS certificate ahead of expiration.'))
    if h.get('server') or h.get('x-powered-by'):
        result.append(finding('disclosure','Server software disclosure','low','Information','Version/platform headers may expose unnecessary infrastructure detail.','Server identification header present','Suppress unnecessary Server and X-Powered-By headers where possible.'))
    else:
        result.append(finding('disclosure','Server software disclosure','pass','Information','No server identification header observed.','Not disclosed','Continue minimizing software identification headers.'))
    cookie_headers=h.get('set-cookie','')
    if cookie_headers:
        per_cookie=[{token.strip().split('=',1)[0] for token in row.lower().split(';')[1:]} for row in cookie_headers.splitlines() if row.strip()]
        result.append(finding('cookie-secure','Secure cookie flag','pass' if all('secure' in flags for flags in per_cookie) else 'medium','Cookies','Secure cookies are limited to HTTPS.','Cookie flags checked (cookie values redacted)','Set Secure on cookies transmitted over HTTPS.'))
        result.append(finding('cookie-http-only','HttpOnly cookie flag','pass' if all('httponly' in flags for flags in per_cookie) else 'medium','Cookies','HttpOnly limits script access to session cookies.','Cookie flags checked (cookie values redacted)','Set HttpOnly for session cookies.'))
        result.append(finding('cookie-samesite','SameSite cookie flag','pass' if all('samesite' in flags for flags in per_cookie) else 'low','Cookies','SameSite can mitigate cross-site request risks.','Cookie flags checked (cookie values redacted)','Specify a suitable SameSite setting on session cookies.'))
    return result


def _request(target: ValidatedTarget, ip: str):
    """Connect to previously validated IP, preserve TLS SNI/hostname validation.

    Never use proxies, URL-based DNS resolution, or connection redirects here.
    """
    raw = socket.create_connection((ip, target.port), timeout=5)
    raw.settimeout(5)
    cert = None
    sock = raw
    try:
        if target.scheme=='https':
            sock = ssl.create_default_context().wrap_socket(raw, server_hostname=target.hostname)
            cert = sock.getpeercert()
        hostname=target.hostname if ':' not in target.hostname else f'[{target.hostname}]'
        tls=None
        if cert:
            exp=ssl.cert_time_to_seconds(cert['notAfter'])
            days=int((exp - datetime.now(timezone.utc).timestamp())/86400)
            tls={'valid':True,'days_remaining':days}
        # HEAD does not consume the page body. Header parser applies line/count caps.
        request = f'HEAD {target.path} HTTP/1.1\r\nHost: {hostname}\r\nUser-Agent: SentinelScan/1.0 (authorized security posture check)\r\nAccept: */*\r\nConnection: close\r\n\r\n'
        sock.sendall(request.encode('ascii','backslashreplace'))
        response=http.client.HTTPResponse(sock)
        response.begin()
        # Cookie values are never stored. Only a placeholder indicating flags.
        headers={}
        cookie_records=[]
        for key,val in response.getheaders():
            lk=key.lower()
            if lk=='set-cookie':
                flags=[]
                for token in val.split(';')[1:]:
                    label=token.strip().split('=')[0].lower()
                    if label in ('secure','httponly','samesite'):
                        flags.append(token.strip().lower()[:40])
                cookie_records.append('cookie=REDACTED; ' + '; '.join(flags))
            elif lk in ('location','content-security-policy','strict-transport-security','x-content-type-options','referrer-policy','permissions-policy','x-frame-options','server','x-powered-by'):
                headers[lk]=val[:1024]
        if cookie_records:
            headers['set-cookie']='\n'.join(cookie_records)
        return {'status':response.status,'headers':headers,'tls':tls}
    finally:
        sock.close()


def scan_target(target: ValidatedTarget, policy: TargetPolicy, transport=None):
    fetch=transport or _request
    visited=set()
    findings=[]
    current=target
    response_code=None
    for hop in range(MAX_REDIRECTS + 1):
        if current.url in visited:
            findings.append(finding('redirect-loop','Redirect loop','medium','Transport','Repeated redirect detected.','Redirect cycle','Remove cyclic redirects.'))
            break
        visited.add(current.url)
        try:
            ip=policy.resolve(current.hostname)
            data=fetch(current,ip)
            response_code=data.get('status',0)
        except (PolicyError, OSError, TimeoutError, ssl.SSLError, http.client.HTTPException, ValueError) as exc:
            findings.append(finding('connection','Connection could not be verified','high','Availability','A safe, complete HTTP/TLS response was not obtained.',type(exc).__name__,'Check network access, DNS and certificate configuration.'))
            break
        if response_code in (301,302,303,307,308) and data.get('headers',{}).get('location'):
            if hop==MAX_REDIRECTS:
                findings.append(finding('redirect-limit','Too many redirects','medium','Transport','Redirect chain exceeded the bounded hop limit.','More than 3 hops','Reduce redirects.'))
                break
            destination=urljoin(current.url,data['headers']['location'])
            try:
                current=policy.validate(destination)
            except PolicyError:
                findings.append(finding('redirect-safety','Blocked unsafe redirect','high','Transport','Redirect leaves authorized or safe targets.','Redirect destination blocked','Review redirects and explicitly authorize only trusted public sites.'))
                break
            continue
        findings.extend(evaluate_headers(data.get('headers',{}),current.scheme,data.get('tls')))
        break
    return {
        'target':target.url,'final_url':current.url,'demo':False,'status':'completed',
        'score':score_findings(findings),'response_code':response_code,
        'scanned_at':datetime.now(timezone.utc).isoformat(), 'findings':findings,
    }
