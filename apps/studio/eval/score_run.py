#!/usr/bin/env python3
"""Score skill-proposed markers against a human-marked run.

    python3 apps/studio/eval/score_run.py <proposals.json> <ground-truth-run-id>

`proposals.json` is whatever the skill wrote — any JSON with a `markers` array of
objects carrying `start`. Keep it OUT of apps/studio/runs/: writing proposals onto
the ground-truth run mixes them into the human record and the test can never be
run again.

Two numbers carry the verdict, and they answer different questions:

  STAR RECALL    — of the moments he cared about, how many had a proposal near?
                   The primary number. A starred moment with no marker near it
                   throws him back into manual culling, which is the cost being
                   removed. Extra markers only cost a keypress.
  STAR PRECISION — how often was a proposal good enough to keep where it stood?
                   Measured by him starring the skill's own marker instead of
                   building his own row beside it.

These cannot share a denominator. A star sitting on a skill marker is at distance
zero by construction, so folding those into recall guarantees a perfect score
however bad the skill is — 500 random timestamps with 8 starred would still read
17/17. They are excluded from recall and reported here instead.

Two confounds this handles, both of which inflate the score if ignored:

1. A star on a *skill marker* is covered by definition. Only stars on clips the
   human created himself are evidence. On video 1 that halves the sample, 17 -> 9.
2. Ground truth folds from labels.jsonl in FILE order, last event per row identity
   wins. Sorting by recordedAt eventually picks the wrong record — video 1's store
   has three pairs written out of timestamp order.
"""
import json
import pathlib
import sys

STUDIO = pathlib.Path(__file__).resolve().parents[1]
if not (STUDIO / "labels.jsonl").is_file():
    # Copied out of the repo. Fall back to the working directory, so the script
    # keeps working from another checkout instead of failing on a stale path.
    for _base in (pathlib.Path.cwd() / "apps/studio", pathlib.Path.cwd()):
        if (_base / "labels.jsonl").is_file():
            STUDIO = _base
            break
TOLERANCES = (20, 30, 45, 60, 90)


def hms(seconds):
    s = int(seconds)
    return "%d:%02d:%02d" % (s // 3600, s % 3600 // 60, s % 60)


def fold_ground_truth(run_id):
    """Human rows for a run. Annotated skill markers and human-added clips are
    returned separately — only the second kind is non-circular evidence."""
    annotated, added = {}, {}
    path = STUDIO / "labels.jsonl"
    for line in path.open(encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        ev = json.loads(line)
        if ev.get("runId") != run_id:
            continue
        verdict = ev.get("verdict")
        if verdict == "annotate" and ev.get("markerIndex") is not None:
            annotated[ev["markerIndex"]] = ev
        start = ev.get("start")
        if start is None:
            continue
        if verdict == "unmiss":
            added.pop(float(start), None)
        elif verdict == "miss":
            added[float(start)] = ev
    return annotated, added


def starred(rows):
    return [r for r in rows if "star" in (r.get("tags") or [])]


def nearest(target, proposals):
    return min(proposals, key=lambda p: abs(p - target))


def recall_table(targets, proposals, label):
    print(f"\n{label} — {len(targets)} moments")
    if not targets:
        print("   none")
        return
    for tol in TOLERANCES:
        hit = sum(1 for t in targets if abs(nearest(t, proposals) - t) <= tol)
        print("   within %2ds: %2d/%2d (%3.0f%%)" % (tol, hit, len(targets), 100 * hit / len(targets)))
    worst = sorted(targets, key=lambda t: -abs(nearest(t, proposals) - t))[:3]
    for t in worst:
        print("   worst: %s — nearest proposal %.0fs away" % (hms(t), abs(nearest(t, proposals) - t)))


def main(argv):
    if len(argv) != 2:
        sys.exit("usage: score_run.py <proposals.json> <ground-truth-run-id>")
    prop_path = pathlib.Path(argv[0])
    run_id = argv[1].removesuffix(".json")
    if prop_path.resolve().parent == (STUDIO / "runs").resolve():
        sys.exit(
            "refusing: proposals are inside apps/studio/runs/. That mixes them into\n"
            "the human record. Move the file somewhere else and rerun."
        )
    proposals = [m["start"] for m in json.loads(prop_path.read_text(encoding="utf-8")).get("markers", [])]
    if not proposals:
        sys.exit("no markers in the proposals file")

    truth_path = STUDIO / "runs" / f"{run_id}.json"
    truth = json.loads(truth_path.read_text(encoding="utf-8"))
    cue_starts = {c["start"] for c in (truth.get("cues") or [])}
    annotated, added = fold_ground_truth(run_id)
    added_rows = list(added.values())
    human_all = sorted([e["start"] for e in annotated.values()] + [r["start"] for r in added_rows])

    print("proposals: %d" % len(proposals))
    print("human rows: %d annotated markers + %d added clips" % (len(annotated), len(added_rows)))

    own_stars = [r["start"] for r in starred(added_rows)]
    starred_markers = starred(list(annotated.values()))
    all_starred = len(own_stars) + len(starred_markers)

    print("\nSTAR PRECISION — proposals kept exactly where the skill put them")
    if proposals and all_starred:
        print("   %d of %d proposals earned a star in place (%.0f%%)" % (
            len(starred_markers), len(proposals), 100 * len(starred_markers) / len(proposals)))
        print("   for scale, %d of %d human rows are starred (%.0f%%)" % (
            all_starred, len(annotated) + len(added_rows),
            100 * all_starred / (len(annotated) + len(added_rows))))
    if starred_markers:
        print("   the exemplars — proposals good enough to bookmark unchanged:")
        for e in sorted(starred_markers, key=lambda x: x["start"]):
            print("      %s  %s" % (hms(e["start"]), (e.get("description") or "")[:56]))
        print("   ^ few-shot material for a skill revision. Excluded from recall below,")
        print("     because their distance to a proposal is zero by construction.")
    recall_table(own_stars, proposals, "STAR RECALL — moments he built himself, so the skill did NOT place them well")
    recall_table(human_all, proposals, "REGION RECALL (every human row)")

    print("\nPRECISION — proposals with no human row nearby")
    for tol in (30, 45, 90):
        hit = sum(1 for p in proposals if abs(nearest(p, human_all) - p) <= tol)
        print("   within %2ds: %2d/%2d land near a human row (%3.0f%%)" % (
            tol, hit, len(proposals), 100 * hit / len(proposals)))

    print("\nDIRECTION — where the nearest proposal sits relative to each added clip")
    offsets = [nearest(r["start"], proposals) - r["start"] for r in added_rows]
    early = sum(1 for o in offsets if o < 0)
    late = sum(1 for o in offsets if o > 0)
    print("   proposal EARLIER, scrub forward: %d" % early)
    print("   proposal LATER,   scrub back:    %d" % late)
    print("   lead   scrub-back cases   median forward scrub")
    for shift in (0, -10, -20, -30, -45, -60):
        moved = [o + shift for o in offsets]
        back = [o for o in moved if o > 0]
        fwd = sorted(-o for o in moved if o <= 0)
        print("   %4ds  %2d of %2d              %3.0fs" % (
            shift, len(back), len(moved), fwd[len(fwd) // 2] if fwd else 0))

    print("\nR-CUE-EXACT — D-032's revert signal")
    off_cue = [p for p in proposals if p not in cue_starts]
    print("   %d/%d proposals land on an exact cue start" % (len(proposals) - len(off_cue), len(proposals)))
    if off_cue:
        print("   off-cue: %s" % ", ".join(hms(p) for p in off_cue[:8]))
        print("   ^ the rule is being ignored — that is a finding, not a curiosity (TD-6)")

    print("\nFALSE POSITIVES to sort into a rejection taxonomy")
    fps = [p for p in proposals if abs(nearest(p, human_all) - p) > 45]
    print("   %d proposals are >45s from any human row:" % len(fps))
    for p in fps:
        print("   %s" % hms(p))


if __name__ == "__main__":
    main(sys.argv[1:])
