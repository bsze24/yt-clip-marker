#!/usr/bin/env python3
"""Merge fetch_transcript.py stdout into a run JSON as `cues`.

Kept as a CLI for runs created outside the in-app ingest path (e.g. by the
yt-clipper skill, which fetches the transcript itself to read it).

Usage:
    python3 apps/studio/attach_cues.py apps/studio/runs/{id}.json transcript.txt
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

GAP_RE = re.compile(r"^>>> GAP (\d+)s @ ")
CUE_RE = re.compile(r"^(\d+:\d+(?::\d+)?)\t(.*)$")


def parse_hms(stamp):
    parts = [int(p) for p in stamp.split(":")]
    if len(parts) == 2:
        minutes, seconds = parts
        return minutes * 60 + seconds
    hours, minutes, seconds = parts
    return hours * 3600 + minutes * 60 + seconds


def parse_transcript(text):
    cues = []
    pending_gap = None
    for raw in text.splitlines():
        line = raw.rstrip("\n")
        gap = GAP_RE.match(line)
        if gap:
            pending_gap = int(gap.group(1))
            continue
        cue = CUE_RE.match(line)
        if not cue:
            continue
        start = float(parse_hms(cue.group(1)))
        entry = {"start": start, "text": cue.group(2).strip()}
        if pending_gap is not None:
            entry["gapBefore"] = pending_gap
            pending_gap = None
        cues.append(entry)
    return cues


def main(argv):
    if len(argv) != 3:
        print("usage: attach_cues.py <run.json> <transcript.txt>", file=sys.stderr)
        return 2
    run_path = Path(argv[1])
    transcript_path = Path(argv[2])
    run = json.loads(run_path.read_text(encoding="utf-8"))
    cues = parse_transcript(transcript_path.read_text(encoding="utf-8"))
    run["cues"] = cues
    run_path.write_text(json.dumps(run, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(cues)} cues → {run_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
