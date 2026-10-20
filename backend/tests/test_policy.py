import socket
from unittest.mock import patch
import pytest

from app.policy import TargetPolicy, PolicyError

@pytest.fixture
def policy():
    return TargetPolicy(['example.com', 'shop.example.com'])

def test_normalizes_public_allowlisted_host(policy):
    result = policy.validate('https://EXAMPLE.COM/path?q=1')
    assert result.hostname == 'example.com'
    assert result.url == 'https://example.com/path?q=1'
    assert result.port == 443

@pytest.mark.parametrize('url', [
    'file:///etc/passwd', 'ftp://example.com', 'https://example.com:8443/',
    'https://any.example.com', 'https://example.com@evil.com',
    'https://u:p@example.com', 'https://example.com/#fragment',
    'http://localhost/', 'https://127.0.0.1/', 'https://example.com\\@evil.com',
])
def test_rejects_invalid_targets(policy, url):
    with pytest.raises(PolicyError):
        policy.validate(url)

def test_disallows_live_scans_until_allowlisted():
    with pytest.raises(PolicyError):
        TargetPolicy([]).validate('https://example.com')

@pytest.mark.parametrize('ip', ['127.0.0.1','192.168.1.20','10.0.0.1','169.254.169.254','::1','fc00::1','fe80::5','100.64.0.1','0.0.0.0','224.0.0.1'])
def test_rejects_unsafe_ip_even_when_dns_returns_it(policy, ip):
    fake = [(socket.AF_INET6 if ':' in ip else socket.AF_INET, socket.SOCK_STREAM, 6, '', (ip, 443))]
    with patch('socket.getaddrinfo', return_value=fake):
        with pytest.raises(PolicyError):
            policy.resolve('example.com')

def test_rejects_mixed_dns_answer(policy):
    answers = [(socket.AF_INET,socket.SOCK_STREAM,6,'',('8.8.8.8',443)),(socket.AF_INET,socket.SOCK_STREAM,6,'',('10.0.0.4',443))]
    with patch('socket.getaddrinfo', return_value=answers):
        with pytest.raises(PolicyError):
            policy.resolve('example.com')

def test_selects_valid_public_ip(policy):
    with patch('socket.getaddrinfo', return_value=[(socket.AF_INET,socket.SOCK_STREAM,6,'',('8.8.8.8',443))]):
        assert policy.resolve('example.com') == '8.8.8.8'

def test_redirect_target_policy_enforced(policy):
    with pytest.raises(PolicyError):
        policy.validate('https://evil.com/from-redirect')
