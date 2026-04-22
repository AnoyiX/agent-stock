from __future__ import annotations

import requests


def http_get_with_proxy_fallback(url: str, **kwargs):
    try:
        return requests.get(url, **kwargs)
    except requests.RequestException as exc:
        if "socks" not in str(exc).lower():
            raise
        with requests.Session() as session:
            session.trust_env = False
            return session.get(url, **kwargs)
