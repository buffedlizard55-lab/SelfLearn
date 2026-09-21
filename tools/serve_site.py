#!/usr/bin/env python3
"""Serve the published site from docs/ for manual review.

The site is static, so reviewing it locally needs nothing more than a file server.
This tool starts one on the loopback interface (or on 0.0.0.0 with --host, for a
container or a forwarded port) and prints the pages worth reading first.

Usage:
    python3 tools/serve_site.py                 # http://127.0.0.1:8000/
    python3 tools/serve_site.py --port 9000
    python3 tools/serve_site.py --host 0.0.0.0  # bind all interfaces
"""

from __future__ import annotations

import argparse
import functools
import http.server
import socketserver
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from selflearn.config import SITE_DIR  # noqa: E402

REVIEW_ORDER = (
    ("index.html", "Overview: what the engine is doing and the run it is showing"),
    ("review.html", "For review: every unresolved irregularity, failure and contradiction"),
    ("library.html", "Library: the questions under research"),
    ("sources.html", "Sources: what was read, what was reachable, what is missing a key"),
    ("experiments.html", "Experiments: what was actually run, and how to repeat it"),
    ("method.html", "Method: the evidence hierarchy, thresholds, criteria and refusals"),
    ("documents.html", "Documents: the hand-written design, architecture and limitation notes"),
    ("requirements.html", "Requirements: the brief traced line by line"),
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--host", default="127.0.0.1", help="interface to bind (default 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="port to bind (default 8000)")
    args = parser.parse_args(argv)

    if not (SITE_DIR / "index.html").exists():
        raise SystemExit(f"No site found at {SITE_DIR}. Build it first: python3 -m selflearn site")

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(SITE_DIR))

    class Server(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True

    with Server((args.host, args.port), handler) as server:
        print(f"serving {SITE_DIR} on http://{args.host}:{args.port}/")
        print("pages to read, in order:")
        for name, note in REVIEW_ORDER:
            marker = "ok " if (SITE_DIR / name).exists() else "missing"
            print(f"  [{marker}] /{name:20} {note}")
        print("press Ctrl+C to stop")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
