"""The hosted read. The client sends an op stream and gets a verdict back."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Iterable, List, Optional, Tuple

from .ops import Op, Verdict

DEFAULT_ENDPOINT = "https://read.embeddedriskanalytics.com/v1/read"
EXPIRY_ENDPOINT = "https://read.embeddedriskanalytics.com/v1/expiry"
DEMO_KEY = "demo"  # rate-limited; get your own key at https://embeddedriskanalytics.com/contact.html


class ReadError(RuntimeError):
    pass


def read(ops: Iterable[Op], supersede: Optional[List[Tuple[str, str]]] = None,
         key: Optional[str] = None, endpoint: Optional[str] = None, timeout: float = 30.0) -> Verdict:
    """Send the ops to the hosted read and return its verdict."""
    key = key or os.environ.get("FATHOM_API_KEY") or DEMO_KEY
    endpoint = endpoint or os.environ.get("FATHOM_ENDPOINT") or DEFAULT_ENDPOINT
    body = json.dumps({"ops": [o.as_dict() for o in ops], "supersede": [list(p) for p in (supersede or [])]}).encode()
    req = urllib.request.Request(endpoint, data=body, method="POST", headers={
        "Content-Type": "application/json", "Authorization": f"Bearer {key}",
        "User-Agent": "fathom-read/0.2.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return Verdict.from_dict(json.loads(r.read().decode()))
    except urllib.error.HTTPError as e:
        msg = e.read().decode(errors="replace")
        if e.code == 401:
            raise ReadError("the read rejected the key; set FATHOM_API_KEY or request one at https://embeddedriskanalytics.com/contact.html") from None
        if e.code == 429:
            raise ReadError("the demo key is rate-limited; request your own at https://embeddedriskanalytics.com/contact.html") from None
        raise ReadError(f"the read returned {e.code}: {msg[:200]}") from None
    except urllib.error.URLError as e:
        raise ReadError(f"could not reach the read at {endpoint}: {e.reason}") from None


def expiry(ops: Iterable[Op], supersede: Optional[List[Tuple[str, str]]] = None, calibration: Optional[str] = None,
           horizon: Optional[int] = None, alarm_multiple: Optional[float] = None,
           key: Optional[str] = None, endpoint: Optional[str] = None, timeout: float = 30.0) -> dict:
    """Send the ops to the hosted expiry read. Returns {"read": verdict dict, "expiry": {...}}.

    The expiry read reports, per step, the hazard that the agent's committed state spoils, the survival curve, the functional
    life remaining in steps, and two alarms, one that fires while a rejected action stands in the record and one that fires on
    committed load alone. Name a calibration for your workload (the service lists them at GET /v1/calibrations); with none named
    the read scores under a pooled default and labels the result a shape rather than a number."""
    key = key or os.environ.get("FATHOM_API_KEY") or DEMO_KEY
    endpoint = endpoint or os.environ.get("FATHOM_EXPIRY_ENDPOINT") or EXPIRY_ENDPOINT
    payload = {"ops": [o.as_dict() for o in ops], "supersede": [list(p) for p in (supersede or [])]}
    if calibration: payload["calibration"] = calibration
    if horizon: payload["horizon_k"] = int(horizon)
    if alarm_multiple: payload["alarm_mult"] = float(alarm_multiple)
    req = urllib.request.Request(endpoint, data=json.dumps(payload).encode(), method="POST", headers={
        "Content-Type": "application/json", "Authorization": f"Bearer {key}", "User-Agent": "fathom-read/0.2.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        msg = e.read().decode(errors="replace")
        if e.code == 401:
            raise ReadError("the read rejected the key; set FATHOM_API_KEY or request one at https://embeddedriskanalytics.com/contact.html") from None
        if e.code == 429:
            raise ReadError("the demo key is rate-limited; request your own at https://embeddedriskanalytics.com/contact.html") from None
        raise ReadError(f"the read returned {e.code}: {msg[:200]}") from None
    except urllib.error.URLError as e:
        raise ReadError(f"could not reach the read at {endpoint}: {e.reason}") from None
