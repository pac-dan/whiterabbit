from __future__ import annotations

from typing import Optional

import os

from flask import current_app


def configure_stripe(stripe_module, *, api_key: Optional[str] = None) -> None:
    """
    Configure Stripe SDK defaults (api key, retries, and request timeout).

    This is especially helpful in hosted environments where transient network issues
    can occur. It also prevents long hangs when DNS or egress is unhealthy.
    """
    key = api_key or current_app.config.get('STRIPE_SECRET_KEY') or os.getenv('STRIPE_SECRET_KEY')
    if key:
        stripe_module.api_key = key

    # Retries: Stripe recommends a small number of automatic retries for transient errors
    # (e.g. intermittent network failures).
    try:
        stripe_module.max_network_retries = int(os.getenv('STRIPE_MAX_NETWORK_RETRIES', '2'))
    except Exception:
        stripe_module.max_network_retries = 2

    # Timeout: keep reasonably short so the request fails fast instead of hanging.
    # Stripe's python lib reads stripe_module.request_timeout.
    try:
        stripe_module.request_timeout = float(os.getenv('STRIPE_REQUEST_TIMEOUT', '15'))
    except Exception:
        stripe_module.request_timeout = 15.0


