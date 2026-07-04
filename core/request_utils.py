"""
Request-level utilities.

Single canonical place to extract the real client IP. Used by login-attempt
logging, HIPAA audit logs, and anywhere else an IP is recorded for security
or compliance purposes — not just cosmetic logging, so it needs to be honest.
"""

from typing import Optional
from ipaddress import ip_address, ip_network

from fastapi import Request

from core.config import settings


def _is_trusted_proxy(peer_ip: Optional[str]) -> bool:
    """True if peer_ip matches a configured trusted proxy IP/CIDR."""
    if not peer_ip or not settings.TRUSTED_PROXY_IPS:
        return False

    try:
        peer = ip_address(peer_ip)
    except ValueError:
        return False

    for entry in settings.TRUSTED_PROXY_IPS:
        try:
            if peer in ip_network(entry, strict=False):
                return True
        except ValueError:
            continue

    return False


def get_client_ip(request: Request) -> str:
    """
    Return the real client IP.

    X-Forwarded-For / X-Real-IP are only honoured when the immediate TCP
    peer (request.client.host) is a configured TRUSTED_PROXY_IPS entry —
    otherwise those headers are attacker-controlled and trusting them lets
    anyone spoof the IP recorded in login-attempt lockouts and audit logs.

    If TRUSTED_PROXY_IPS isn't configured yet, this always falls back to the
    raw TCP peer IP (e.g. your load balancer's IP) — less useful, but honest,
    rather than trusting an unverified header.
    """
    peer_ip = request.client.host if request.client else None

    if _is_trusted_proxy(peer_ip):
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

    return peer_ip or "0.0.0.0"