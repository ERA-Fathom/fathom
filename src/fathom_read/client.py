"""The hosted read. The client sends an op stream and gets a verdict back."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Iterable, List, Optional, Tuple

from .ops import Op, Verdict

DEFAULT_ENDPOINT = "https://read.embeddedriskanalytics.com/v1/read"
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
        "User-Agent": "fathom-read/0.1.0"})
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
