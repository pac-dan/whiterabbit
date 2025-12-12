from __future__ import annotations

import json
import os
import time
from typing import Optional, Any

from flask import current_app

_DEBUG_LOG_PATH = r"c:\Users\Dan\whiterabbit\.cursor\debug.log"


def _agent_log(hypothesis_id: str, location: str, message: str, data: dict) -> None:
    # region agent log
    try:
        payload = {
            "sessionId": "debug-session",
            "runId": os.getenv("AGENT_RUN_ID", "pre-fix"),
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data,
            "timestamp": int(time.time() * 1000),
        }
        with open(_DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass
    # endregion agent log


def _key_kind(key: Optional[str]) -> str:
    if not key:
        return "none"
    if key.startswith("sk_test_"):
        return "sk_test"
    if key.startswith("sk_live_"):
        return "sk_live"
    return "other"


_UNSET = object()


def configure_stripe(stripe_module, *, api_key: Any = _UNSET) -> None:
    """
    FIXED (H1): Always overwrites stripe_module.api_key (including setting it to None)
    to prevent stale values leaking across requests/greenlets.
    """
    config_key = current_app.config.get("STRIPE_SECRET_KEY")
    env_key = os.getenv("STRIPE_SECRET_KEY")

    api_key_param_provided = api_key is not _UNSET
    if api_key_param_provided:
        chosen_key = api_key  # may be None intentionally
        chosen_source = "explicit"
    elif config_key:
        chosen_key = config_key
        chosen_source = "flask_config"
    elif env_key:
        chosen_key = env_key
        chosen_source = "env"
    else:
        chosen_key = None
        chosen_source = "none"

    _agent_log(
        "H1",
        "app/utils/stripe_helpers.py:configure_stripe:entry",
        "configure_stripe (fixed) entry",
        {
            "stripe_api_key_was_set": bool(getattr(stripe_module, "api_key", None)),
            "api_key_param_provided": api_key_param_provided,
            "chosen_source": chosen_source,
            "chosen_key_kind": _key_kind(chosen_key if isinstance(chosen_key, str) else None),
        },
    )

    # FIX: always overwrite
    stripe_module.api_key = chosen_key if isinstance(chosen_key, str) else None

    _agent_log(
        "H1",
        "app/utils/stripe_helpers.py:configure_stripe:exit",
        "configure_stripe (fixed) exit",
        {"stripe_api_key_is_set": bool(getattr(stripe_module, "api_key", None))},
    )

    # Keep other stripe network settings (not part of the bug) consistent
    try:
        stripe_module.max_network_retries = int(os.getenv("STRIPE_MAX_NETWORK_RETRIES", "2"))
    except Exception:
        stripe_module.max_network_retries = 2
    try:
        stripe_module.request_timeout = float(os.getenv("STRIPE_REQUEST_TIMEOUT", "15"))
    except Exception:
        stripe_module.request_timeout = 15.0


