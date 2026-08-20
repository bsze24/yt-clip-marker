#!/usr/bin/env python3
"""Turn a studio run into the text file the yt-clipper skill expects.

The skill's step 1 shells out to yt-dlp for a YouTube caption track. Video 2 came
from a Zoom export and has no captioned YouTube identity (D-036), and none of the
four YouTube uploads has captions at all. But the skill does not need the URL — it
needs the file that script prints, and a run already holds everything in it.

    python3 apps/studio/eval/make_transcript.py <run-id> [gap-seconds] > out.txt

The gap threshold defaults to ingest.DEFAULT_GAP_SECONDS, the same number the studio
used when it built the run. Hardcoding a different one meant the skill saw 20 GAP
lines where the studio showed 26 flagged cues on the same video — the two views of
one transcript disagreeing for no reason.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import ingest  # noqa: E402  — for DEFAULT_GAP_SECONDS, so the skill and the studio agree

RUNS = pathlib.Path(__file__).resolve().parents[1] / "runs"


def resolve_run(arg):
    """Accept a run id, a filename, or a path. Resolving only against the script's
    own location breaks the moment the file is copied somewhere else, which is
    exactly what happens when you want to run it from another checkout."""
    direct = pathlib.Path(arg)
    if direct.is_file():
        return direct
    for base in (RUNS, pathlib.Path.cwd() / "apps/studio/runs", pathlib.Path.cwd()):
        candidate = base / f"{arg.removesuffix('.json')}.json"
        if candidate.is_file():
            return candidate
    sys.exit(f"no such run: {arg}")


def hms(seconds):
    s = int(seconds)
    return "%02d:%02d:%02d" % (s // 3600, s % 3600 // 60, s % 60)


def render(cues, gap_threshold=None):
    """Prefer the `gapBefore` the run already carries.

    Recomputing from `cues[]` gets a slightly different answer, because ingest
    measured the gaps on the raw sub-second starts and then rounded the starts
    to whole seconds. Recomputing off the rounded values gave 28 GAP lines where
    the run holds 26 — the skill and the studio disagreeing about one transcript.
    Only fall back to recomputing for a run old enough to predate the flags.
    """
    have_flags = any("gapBefore" in c for c in cues)
    lines = []
    prev = None
    for cue in cues:
        start = cue["start"]
        gap = cue.get("gapBefore")
        if not have_flags and prev is not None and gap_threshold is not None:
            if start - prev >= gap_threshold:
                gap = int(start - prev)
        if gap:
            lines.append(">>> GAP %ds @ %s" % (int(gap), hms(start)))
        lines.append("%s\t%s" % (hms(start), cue.get("text", "")))
        prev = start
    return lines


def main(argv):
    if not argv:
        sys.exit("usage: make_transcript.py <run-id> [gap-seconds]")
    threshold = int(argv[1]) if len(argv) > 1 else ingest.DEFAULT_GAP_SECONDS
    path = resolve_run(argv[0])
    run = json.loads(path.read_text(encoding="utf-8"))
    cues = run.get("cues") or []
    if not cues:
        sys.exit(f"{run_id} has zero cues — nothing to hand the skill")
    lines = render(cues, threshold)
    gaps = sum(1 for line in lines if line.startswith(">>> GAP"))
    print("\n".join(lines))
    print(
        f"# {len(lines)} lines, {gaps} GAP flags, threshold {threshold}s",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main(sys.argv[1:])
