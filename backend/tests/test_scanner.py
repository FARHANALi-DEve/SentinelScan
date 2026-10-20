from unittest.mock import patch
from app.policy import TargetPolicy
from app.scanner import evaluate_headers, score_findings, scan_target
from app.demo import demo_result

GOOD = {'content-security-policy': "default-src 'self'",'strict-transport-security':'max-age=63072000; includeSubDomains','x-content-type-options':'nosniff','referrer-policy':'strict-origin-when-cross-origin','permissions-policy':'camera=()','x-frame-options':'DENY'}

def test_missing_headers_generate_actionable_findings():
    findings = evaluate_headers({}, 'https', {'valid':True,'days_remaining':90})
    assert any(f['check_id']=='csp' and f['severity']=='high' and f['recommendation'] for f in findings)
    assert any(f['check_id']=='hsts' and f['severity']=='medium' for f in findings)
    assert 0 <= score_findings(findings) < 100

def test_good_headers_produce_positive_score():
    findings = evaluate_headers(GOOD, 'https', {'valid':True,'days_remaining':90})
    assert score_findings(findings)==100

def test_cookie_evidence_does_not_leak_session_value():
    findings = evaluate_headers(dict(GOOD, **{'set-cookie':'session=supersecret; Path=/'}), 'https', {'valid':True,'days_remaining':90})
    assert any(f['check_id']=='cookie-secure' for f in findings)
    assert 'supersecret' not in str(findings)

def test_demo_is_deterministic_and_offline():
    assert demo_result()['demo'] is True
    assert demo_result()['score'] == demo_result()['score']
    assert len(demo_result()['findings']) >= 7

def test_redirect_to_disallowed_host_is_never_fetched():
    policy = TargetPolicy(['example.com'])
    requests=[]
    def transport(target, ip):
        requests.append(target.url)
        return {'status':302,'headers':{'location':'http://localhost/admin'},'tls':{'valid':True,'days_remaining':60}}
    with patch.object(policy,'resolve',return_value='8.8.8.8'):
        result=scan_target(policy.validate('https://example.com'),policy,transport)
    assert len(requests)==1
    assert any(f['check_id']=='redirect-safety' and f['severity']=='high' for f in result['findings'])

def test_pinned_ip_passed_to_transport():
    policy=TargetPolicy(['example.com'])
    ips=[]
    def transport(target, ip):
        ips.append(ip)
        return {'status':200,'headers':GOOD,'tls':{'valid':True,'days_remaining':90}}
    with patch.object(policy,'resolve',return_value='8.8.8.8'):
        result=scan_target(policy.validate('https://example.com'),policy,transport)
    assert ips==['8.8.8.8']
    assert result['score']==100


def test_tls_network_failure_gives_visible_finding():
    policy=TargetPolicy(['example.com'])
    def fail(target, ip):
        raise OSError('connection refused')
    with patch.object(policy,'resolve',return_value='8.8.8.8'):
        result=scan_target(policy.validate('https://example.com'),policy,fail)
    assert result['score'] < 100
    assert any(f['check_id']=='connection' for f in result['findings'])

def test_secure_cookie_requires_exact_attribute():
    import app.scanner as scanner
    bad = dict(GOOD, **{'set-cookie':'session=REDACTED; Securely; SameSite=Lax'})
    findings=scanner.evaluate_headers(bad,'https',{'valid':True,'days_remaining':90})
    secure=next(f for f in findings if f['check_id']=='cookie-secure')
    assert secure['severity']=='medium'


def test_transport_connects_only_to_pinned_ip(monkeypatch):
    import app.scanner as scanner
    from app.policy import ValidatedTarget
    events=[]
    class FakeSocket:
        def settimeout(self,t):pass
        def sendall(self,raw):events.append(('request',raw))
        def getpeercert(self):return {'notAfter':'Jan  1 00:00:00 2033 GMT'}
        def close(self):pass
    class FakeContext:
        def wrap_socket(self,sock,server_hostname):events.append(('sni',server_hostname));return sock
    class FakeResponse:
        def __init__(self,sock):pass
        def begin(self):pass
        status=200
        def getheaders(self):return [('Content-Security-Policy',"default-src 'self'")]
    monkeypatch.setattr(scanner.socket,'create_connection',lambda address,timeout:events.append(('connect',address)) or FakeSocket())
    monkeypatch.setattr(scanner.ssl,'create_default_context',lambda:FakeContext())
    monkeypatch.setattr(scanner.http.client,'HTTPResponse',FakeResponse)
    t=ValidatedTarget('https://example.com/x','example.com','https',443,'/x')
    assert scanner._request(t,'8.8.8.8')['status']==200
    assert ('connect',('8.8.8.8',443)) in events
    assert ('sni','example.com') in events
    assert b'Host: example.com' in [v for k,v in events if k=='request'][0]

def test_all_cookies_must_have_secure_and_httponly_flags():
    headers=dict(GOOD, **{'set-cookie':'a=REDACTED; Secure; HttpOnly; SameSite=Lax\nb=REDACTED; SameSite=Lax'})
    findings=evaluate_headers(headers,'https',{'valid':True,'days_remaining':90})
    assert next(f for f in findings if f['check_id']=='cookie-secure')['severity']=='medium'
    assert next(f for f in findings if f['check_id']=='cookie-http-only')['severity']=='medium'
    assert 'REDACTED' not in str(findings)
