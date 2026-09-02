from __future__ import annotations

import argparse
import json
import os
import sys
from typing import List, Optional, Tuple

from . import adapters
from .client import DEMO_KEY, ReadError, read
from .ops import Op, Verdict

EXAMPLES = os.path.join(os.path.dirname(__file__), "examples")


def load_ops(path: str, fmt: str = "auto", mapping_path: Optional[str] = None) -> List[Op]:
    with open(path) as f:
        text = f.read()
    if path.endswith(".jsonl"):
        return adapters.events.load_jsonl(text)
    doc = json.loads(text)
    if fmt == "auto":
        fmt = adapters.detect(doc)
    if fmt not in adapters.FORMATS:
        raise SystemExit(f"unknown format {fmt!r}; run `fathom formats`")
    return adapters.FORMATS[fmt].load(doc, mapping_path=mapping_path)


def parse_supersede(items: Optional[List[str]]) -> List[Tuple[str, str]]:
    out = []
    for it in items or []:
        if "=" not in it:
            raise SystemExit(f"--supersede expects old=new, got {it!r}")
        old, new = it.split("=", 1)
        out.append((old.strip(), new.strip()))
    return out


def render(verdict: Verdict, title: str = "") -> str:
    lines = []
    if title:
        lines.append(title)
    lines.append(f"ops read: {verdict.ops_read}   rejected (no-ops): {verdict.ops_rejected}   live facts: {verdict.live_facts}")
    if verdict.coherent:
        lines.append("committed state: coherent. No action contradicted an earlier commitment.")
        return "\n".join(lines)
    lines.append(f"committed state: {len(verdict.findings)} finding{'s' if len(verdict.findings) != 1 else ''}")
    for f in verdict.findings:
        where = f"step {f.step}" if f.step is not None else "end of run"
        cite = f" (cites step {f.cites})" if f.cites is not None else ""
        lines.append(f"  [{f.kind}] {where}{cite}: {f.detail}")
    return "\n".join(lines)


def _read(ops, supersede, args) -> Verdict:
    try:
        return read(ops, supersede=supersede, key=args.key, endpoint=args.endpoint)
    except ReadError as e:
        raise SystemExit(f"fathom: {e}")


def cmd_read(args) -> int:
    ops = load_ops(args.path, args.format, args.map)
    if args.ops:
        print(json.dumps([o.as_dict() for o in ops], indent=2))
        return 0
    v = _read(ops, parse_supersede(args.supersede), args)
    if args.json:
        print(json.dumps(v.as_dict(), indent=2))
    else:
        print(render(v, os.path.basename(args.path)))
    return 0 if v.coherent else 2


def cmd_demo(args) -> int:
    print("fathom demo: a coding agent renames guest_id to customer_id across five files, then runs the tests.\n")
    for name in ("rename_coherent.json", "rename_starved.json"):
        ops = load_ops(os.path.join(EXAMPLES, name), "edits")
        v = _read(ops, [("guest_id", "customer_id")], args)
        print(render(v, f"== {name}"))
        print()
    print("Both runs reported success and a green test suite. Only one of them renamed the field.")
    print("Try it on your own trace:  fathom read path/to/trace.json --supersede old=new")
    return 0


def cmd_formats(args) -> int:
    for name, mod in adapters.FORMATS.items():
        doc = (mod.__doc__ or "").strip().splitlines()[0] if mod.__doc__ else ""
        print(f"{name:14s} {doc}")
    return 0


def _common(p):
    p.add_argument("--key", help="your read key (or set FATHOM_API_KEY); the demo key is rate-limited")
    p.add_argument("--endpoint", help=argparse.SUPPRESS)


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(prog="fathom", description="Catch the step where an AI agent contradicts a decision it already made.")
    sub = p.add_subparsers(dest="cmd")

    r = sub.add_parser("read", help="read a trace and report contradictions of committed state")
    r.add_argument("path", help="trace file (.json or .jsonl)")
    r.add_argument("--format", default="auto", help="events | edits | openinference | langgraph | crewai | letta | dbos (default: auto)")
    r.add_argument("--supersede", action="append", metavar="OLD=NEW", help="a token the run should have replaced, e.g. guest_id=customer_id (repeatable)")
    r.add_argument("--map", help="JSON file mapping your tool or step names to ops")
    r.add_argument("--json", action="store_true", help="print the verdict as JSON")
    r.add_argument("--ops", action="store_true", help="print the op stream the adapter produced and stop (nothing is sent)")
    _common(r)
    r.set_defaults(fn=cmd_read)

    d = sub.add_parser("demo", help="run the bundled rename example, coherent and not")
    _common(d)
    d.set_defaults(fn=cmd_demo)

    f = sub.add_parser("formats", help="list the trace formats the adapters accept")
    f.set_defaults(fn=cmd_formats)

    args = p.parse_args(argv)
    if not args.cmd:
        p.print_help()
        return 1
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
