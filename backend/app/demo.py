"""Deterministic, fully offline sample of a website posture scan."""
from .scanner import evaluate_headers, score_findings, finding

_SAMPLE_HEADERS = {
    'content-security-policy': "default-src 'self'",
    'x-content-type-options':'nosniff',
    'referrer-policy':'strict-origin-when-cross-origin',
    'server':'nginx',
    'set-cookie':'session=REDACTED; Secure; HttpOnly; SameSite=Lax',
}

def demo_result():
    checks=evaluate_headers(_SAMPLE_HEADERS,'https',{'valid':True,'days_remaining':76})
    checks.append(finding('redirect','HTTPS redirect verified','pass','Transport','Traffic can be upgraded to HTTPS.','HTTPS supported','Keep automatic HTTPS redirects configured.'))
    return {
        'target':'https://acme-demo.example', 'final_url':'https://acme-demo.example',
        'demo':True, 'status':'completed', 'score':score_findings(checks),
        'response_code':200,'findings':checks,
    }
