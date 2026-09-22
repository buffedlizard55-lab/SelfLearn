#!/usr/bin/env python3
"""Reject a topic without destroying its history.

    python3 tools/reject_topic.py --id topic-3f1faf16146a --reason "..." [--link URL]

The library is append-only, so rejecting a topic means writing a new record for
the same primary key with a later timestamp and ``status="rejected"``. The old
record stays in ``library/topics.jsonl``; ``Library.active_topics()`` filters
rejected topics out of the plan and out of the published site, and the reason is
stored on the record so a reviewer can see why it went.

This is the reviewer's half of the "flag irregularities for review" requirement:
a finding can be closed with a reason and a link, and the original text is never
overwritten.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from selflearn.learn.store import Library  # noqa: E402
from selflearn.models import Irregularity  # noqa: E402
from selflearn.util import stable_id, utcnow_iso  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mark a topic rejected, with a recorded reason.")
    parser.add_argument("--id", dest="topic_id", required=True, help="topic_id as printed by 'selflearn status --topics'")
    parser.add_argument("--reason", required=True, help="why it is rejected; stored on the record")
    parser.add_argument("--link", default="", help="optional URL supporting the decision")
    parser.add_argument("--root", default=str(ROOT), help="library root (defaults to the repository)")
    parser.add_argument("--list", action="store_true", help="list topics and exit")
    args = parser.parse_args(argv)

    root = Path(args.root)
    library = Library.load(root, run_id=f"reject-{utcnow_iso()[:10]}")

    if args.list or args.topic_id == "-":
        for topic in sorted(library.topics.values(), key=lambda t: t.topic_id):
            print(f"{topic.topic_id:44} {topic.status:12} {topic.origin:10} {topic.title}")
        return 0

    topic = library.topics.get(args.topic_id)
    if topic is None:
        print(f"no topic with id {args.topic_id}", file=sys.stderr)
        return 1

    previous_status = topic.status
    topic.status = "rejected"
    topic.last_updated = utcnow_iso()
    topic.notes = (
        f"Rejected {topic.last_updated} (was '{previous_status}'). Reason: {args.reason}"
        + (f" Reference: {args.link}" if args.link else "")
        + (f" Previous note: {topic.notes}" if topic.notes else "")
    )
    library.add_topics([topic])
    library.add_irregularities(
        [
            Irregularity(
                irregularity_id=stable_id("irr", "reject", topic.topic_id, args.reason[:60]),
                severity="info",
                stage="review",
                topic_id=topic.topic_id,
                summary=f"Topic {topic.topic_id} rejected by a reviewer",
                detail=args.reason + (f" Reference: {args.link}" if args.link else ""),
                url=args.link or None,
                suggested_action="The record stays in library/topics.jsonl; the topic is excluded from planning and from the site.",
                resolved=True,
            )
        ]
    )
    print(f"rejected {topic.topic_id} ('{topic.title}'); rebuild the site with 'python3 -m selflearn site'")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
