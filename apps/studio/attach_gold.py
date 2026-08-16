#!/usr/bin/env python3
"""Fetch a video's YouTube description and attach parsed timestamp labels to a run.

Kept as a CLI for runs created outside the in-app ingest path (e.g. by the
yt-clipper skill). Fetching and parsing live in ingest.py.

Usage:
    python3 apps/studio/attach_gold.py apps/studio/runs/{id}.json [youtube-url]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from ingest import (
    IngestError,
    fetch_title_and_description,
    parse_description_timestamps,
    parse_video_id,
)


def main(argv):
    if len(argv) < 2:
        print("usage: attach_gold.py <run.json> [youtube-url]", file=sys.stderr)
        return 2
    run_path = Path(argv[1])
    run = json.loads(run_path.read_text(encoding="utf-8"))
    url = argv[2] if len(argv) > 2 else run.get("url")
    video_id = parse_video_id(url or "")
    if not video_id:
        print("no parseable url on run and none passed", file=sys.stderr)
        return 2
    try:
        _title, description = fetch_title_and_description(video_id)
    except IngestError as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1
    gold = parse_description_timestamps(description)
    run["descriptionText"] = description
    run["gold"] = gold
    run_path.write_text(json.dumps(run, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(gold)} description timestamps → {run_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
