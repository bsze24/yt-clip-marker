#!/usr/bin/env python3
"""Attach extracted YouTube-description timestamps to a studio run.

Kept as a CLI for runs created outside the in-app ingest path (e.g. by the
yt-clipper skill). It also losslessly migrates the deprecated data key without
refetching the description. Fetching and parsing live in ingest.py.

Usage:
    python3 apps/studio/attach_extracted.py apps/studio/runs/{id}.json [youtube-url]
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


def migrate_deprecated_key(run):
    """Migrate in memory, returning a status string or None when no migration applies."""
    if "gold" not in run:
        return None
    if "extracted" in run and run["extracted"] != run["gold"]:
        raise ValueError("run has conflicting gold[] and extracted[]; refusing to choose")
    if "extracted" not in run:
        run["extracted"] = run["gold"]
        action = "migrated gold[] → extracted[]"
    else:
        action = "removed duplicate gold[]"
    run.pop("gold")
    return action


def main(argv):
    if len(argv) < 2:
        print("usage: attach_extracted.py <run.json> [youtube-url]", file=sys.stderr)
        return 2
    run_path = Path(argv[1])
    run = json.loads(run_path.read_text(encoding="utf-8"))

    try:
        action = migrate_deprecated_key(run)
    except ValueError as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1
    if action:
        run_path.write_text(
            json.dumps(run, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"{action} in {run_path}")
        return 0

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
    extracted = parse_description_timestamps(description)
    run["descriptionText"] = description
    run["extracted"] = extracted
    run_path.write_text(json.dumps(run, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(extracted)} description timestamps → {run_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
