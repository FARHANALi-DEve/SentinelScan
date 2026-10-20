"""Network-safety policy for strictly allowlisted, public website scans."""
from dataclasses import dataclass
import ipaddress
import re
import socket
from urllib.parse import urlsplit, urlunsplit

class PolicyError(ValueError):
    """Unsafe or unauthorized scan destination."""

@dataclass(frozen=True)
class ValidatedTarget:
    url: str
    hostname: str
    scheme: str
    port: int
    path: str

_HOST = re.compile(r'^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)(?:\.(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?))*$')

class TargetPolicy:
    def __init__(self, allowed_hosts):
        self.allowed_hosts = {h.strip().lower().rstrip('.') for h in allowed_hosts if h.strip()}

    def validate(self, raw_url: str) -> ValidatedTarget:
        if not isinstance(raw_url, str) or not raw_url or len(raw_url) > 2048 or any(ord(c) < 32 or c == '\\' for c in raw_url):
            raise PolicyError('Provide a valid HTTP(S) URL of at most 2048 characters.')
        try:
            parsed = urlsplit(raw_url)
            hostname = (parsed.hostname or '').lower().rstrip('.')
            port = parsed.port
        except ValueError as exc:
            raise PolicyError('URL contains an invalid hostname or port.') from exc
        if parsed.scheme not in ('http', 'https') or not parsed.netloc:
            raise PolicyError('Only HTTP and HTTPS website URLs are supported.')
        if parsed.username is not None or parsed.password is not None or parsed.fragment:
            raise PolicyError('URL credentials and fragments are not permitted.')
        if not hostname or not (_HOST.fullmatch(hostname) or _public_literal(hostname)) or '..' in hostname:
            raise PolicyError('URL hostname is invalid.')
        default_port = 443 if parsed.scheme == 'https' else 80
        if port is not None and port != default_port:
            raise PolicyError('Only standard HTTP/HTTPS ports are permitted.')
        if hostname not in self.allowed_hosts:
            raise PolicyError('Target host is not in ALLOWED_TARGET_HOSTS. Only scan sites you control.')
        path = parsed.path or '/'
        netloc = f'[{hostname}]' if ':' in hostname else hostname
        return ValidatedTarget(urlunsplit((parsed.scheme, netloc, path, parsed.query, '')), hostname, parsed.scheme, default_port, path + ('?' + parsed.query if parsed.query else ''))

    def resolve(self, hostname: str) -> str:
        """Fail closed on all DNS answers if even one address is not public.

        The caller MUST connect to the returned IP, not resolve the domain again.
        """
        try:
            addresses = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
        except (socket.gaierror, OSError) as exc:
            raise PolicyError('DNS resolution failed for the approved host.') from exc
        if not addresses:
            raise PolicyError('DNS returned no addresses.')
        public = []
        for answer in addresses:
            ip_text = answer[4][0]
            try:
                address = ipaddress.ip_address(ip_text)
            except ValueError as exc:
                raise PolicyError('DNS returned a malformed address.') from exc
            if not address.is_global or address.is_multicast or address.is_reserved or address.is_link_local or address.is_loopback:
                raise PolicyError('DNS returned a non-public IP address. Scan blocked.')
            public.append(str(address))
        return public[0]

def _public_literal(hostname: str) -> bool:
    try:
        ipaddress.ip_address(hostname)
        return True  # Public/private decision occurs in resolve().
    except ValueError:
        return False
