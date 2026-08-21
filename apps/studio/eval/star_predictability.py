#!/usr/bin/env python3
"""Does anything in the transcript predict which clips Brian starred?

    python3 apps/studio/eval/star_predictability.py

The question `EVAL.md` §7E asks, answered 2026-08-21. Same shape as the `take`
test that produced [[D-040]]: pick features a model could compute from text
alone, score each against the human's stars, compare to the base rate. A
feature is dead if its AUC sits near 0.50 and does not keep its sign across the
three lessons.

Four parts, and the third is the one that decides it:

  1. TEN TRANSCRIPT FEATURES over a window around each clip.
  2. CONFOUND CHECK on the only feature that beat chance (position in lesson).
  3. CEILING — an LLM scored all 75 of video 2's clips from Brian's OWN labels,
     stars hidden. His label is a strictly richer input than the transcript: it
     is his description of the moment, written after he saw it. If that cannot
     separate starred from unstarred, nothing computed from the transcript can.
  4. WHAT star ACTUALLY TRACKS — tag and label-word lift.

Population: clips Brian created himself (verdict `miss`, latest per start,
minus `unmiss`) plus, where they exist, skill markers he annotated. Only rows
carrying tags can carry a star; `relabel` events carry no tags and cannot
change one.

Verdict recorded in [[D-044]].
"""
import collections
import json
import pathlib
import random
import re
import statistics

STUDIO = pathlib.Path(__file__).resolve().parents[1]
RUNS = {
    "video1": "YYW4Q1Nivg8-20260814-1248",
    "video2": "GMT20260730-155336_Recording_640x360-1-20260819-0903",
    "video3": "GMT20260712-220424_Recording_640x360-20260819-1303",
}
WINDOW_BACK, WINDOW_AHEAD = 15, 60

THEORY = re.compile(r"\b(chord|chords|minor|major|diminished|dominant|voicing|voicings|"
                    r"melody|melodic|harmon\w+|inversion|inversions|triad|triads|scale|"
                    r"tritone|sus|bebop|blues|resolution|resolv\w+|key|modulat\w+|"
                    r"seventh|sixth|flat|sharp|root|bass|tension|rhythm|beat|tempo|"
                    r"phrase|phrasing|line|lines|note|notes|tone|tones|pentatonic|"
                    r"2-5|two-five|turnaround|form|bridge|chorus|verse)\b", re.I)
INSTRUCT = re.compile(r"\b(try|play|do that|practice|exercise|should|let's|listen|"
                      r"start with|go back|again|work on|homework|the way to|you want to|"
                      r"you have to|make sure|think of)\b", re.I)
EMPHASIS = re.compile(r"\b(important|importantly|the point|the whole|really matters|magical|"
                      r"beautiful|always|never|key thing|big|huge|crucial|the main|"
                      r"perfect|amazing|love that|that's it)\b", re.I)

# Produced blind: the model read video 2's 75 labels in time order with the star
# tags withheld and scored each 0-10 for "Brian would star this", then this
# vector was scored against the store. Kept verbatim so the result is checkable.
LLM_SCORES = [
    6, 4, 6, 7, 5, 8, 7, 1, 1, 3, 4, 4, 6, 6, 5, 9, 5, 4, 6, 5, 7, 6, 1, 3, 5,
    1, 6, 4, 3, 4, 6, 5, 4, 6, 4, 2, 6, 6, 2, 6, 4, 6, 3, 2, 5, 7, 5, 7, 7, 7,
    5, 2, 5, 5, 6, 6, 4, 6, 6, 2, 3, 8, 8, 7, 6, 8, 6, 6, 6, 9, 5, 8, 3, 8, 6,
]


def fold(run_id):
    """Human rows for a run. Added clips and annotated skill markers separately."""
    added, annotated = {}, {}
    for line in (STUDIO / "labels.jsonl").open(encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        ev = json.loads(line)
        if ev.get("runId") != run_id:
            continue
        if ev.get("verdict") == "annotate" and ev.get("markerIndex") is not None:
            annotated[ev["markerIndex"]] = ev
        start = ev.get("start")
        if start is None:
            continue
        if ev.get("verdict") == "unmiss":
            added.pop(float(start), None)
        elif ev.get("verdict") == "miss":
            added[float(start)] = ev
    return list(added.values()), list(annotated.values())


def is_star(row):
    return "star" in (row.get("tags") or [])


def auc(pairs):
    """Rank AUC with ties at half credit. None when one class is empty."""
    pos = [s for s, y in pairs if y]
    neg = [s for s, y in pairs if not y]
    if not pos or not neg:
        return None
    total = sum(1.0 if p > n else (0.5 if p == n else 0.0) for p in pos for n in neg)
    return total / (len(pos) * len(neg))


def permutation_p(pairs, observed, trials=4000, seed=7):
    rnd = random.Random(seed)
    labels = [y for _, y in pairs]
    scores = [s for s, _ in pairs]
    dev = abs(observed - 0.5)
    hits = 0
    for _ in range(trials):
        rnd.shuffle(labels)
        a = auc(list(zip(scores, labels)))
        if a is not None and abs(a - 0.5) >= dev:
            hits += 1
    return (hits + 1) / (trials + 1)


def features(start, cues, duration, gap_starts):
    lo, hi = start - WINDOW_BACK, start + WINDOW_AHEAD
    win = [c for c in cues if lo <= c["start"] <= hi]
    bodies, teacher_words, total_words = [], 0, 0
    for cue in win:
        text = cue.get("text", "")
        m = re.match(r"^([^:]{1,24}):\s*(.*)$", text)
        who, body = (m.group(1), m.group(2)) if m else (None, text)
        n = len(body.split())
        total_words += n
        if who and "jake" in who.lower():
            teacher_words += n
        bodies.append(body)
    body_text = " ".join(bodies)
    words = body_text.split()
    nw = max(len(words), 1)
    return {
        "words_per_sec": len(words) / max(hi - lo, 1),
        "teacher_share": (teacher_words / total_words) if total_words else 0.0,
        "theory_per_100w": 100 * len(THEORY.findall(body_text)) / nw,
        "instruct_per_100w": 100 * len(INSTRUCT.findall(body_text)) / nw,
        "emphasis_per_100w": 100 * len(EMPHASIS.findall(body_text)) / nw,
        "question_per_100w": 100 * body_text.count("?") / nw,
        "mean_cue_chars": statistics.mean([len(b) for b in bodies]) if bodies else 0.0,
        "vocab_richness": len(set(w.lower() for w in words)) / nw,
        "near_silence_gap": 1.0 if any(abs(g - start) <= 30 for g in gap_starts) else 0.0,
        "position_in_lesson": start / duration if duration else 0.0,
    }


def load(kind="added"):
    per_video, pooled = {}, []
    for name, run_id in RUNS.items():
        run = json.loads((STUDIO / "runs" / f"{run_id}.json").read_text(encoding="utf-8"))
        cues = run.get("cues") or []
        duration = max((c["start"] for c in cues), default=0)
        gap_starts = [c["start"] for c in cues if c.get("gapBefore")]
        added, annotated = fold(run_id)
        rows = added if kind == "added" else annotated
        recs = [(features(float(r["start"]), cues, duration, gap_starts), 1 if is_star(r) else 0)
                for r in rows]
        per_video[name] = recs
        pooled.extend(recs)
    return per_video, pooled


def part1():
    print("=" * 78)
    print("1. TEN TRANSCRIPT FEATURES — clips Brian created himself")
    print("=" * 78)
    per_video, pooled = load("added")
    for name, recs in per_video.items():
        p = sum(y for _, y in recs)
        print("   %-8s %3d clips, %2d starred (%.0f%%)" % (name, len(recs), p, 100 * p / len(recs)))
    p = sum(y for _, y in pooled)
    print("   POOLED   %3d clips, %2d starred — base rate %.0f%%" % (
        len(pooled), p, 100 * p / len(pooled)))
    print("\n   %-22s%11s%9s   per-video AUC" % ("feature", "pooled AUC", "p(perm)"))
    for f in pooled[0][0]:
        pairs = [(x[f], y) for x, y in pooled]
        a = auc(pairs)
        per = " ".join("%.2f" % auc([(x[f], y) for x, y in recs]) for recs in per_video.values())
        print("   %-22s%11.3f%9.3f   %s" % (f, a, permutation_p(pairs, a), per))
    print("\n   AUC 0.50 is a coin flip. The sign must hold across all three columns")
    print("   for a feature to be real rather than one lesson's noise.")


def part2():
    print("\n" + "=" * 78)
    print("2. CONFOUND — is position_in_lesson content, or the annotation pass?")
    print("=" * 78)
    for name, run_id in RUNS.items():
        run = json.loads((STUDIO / "runs" / f"{run_id}.json").read_text(encoding="utf-8"))
        duration = max((c["start"] for c in run.get("cues") or []), default=1)
        rows = sorted(fold(run_id)[0], key=lambda r: r["recordedAt"])
        forward = sum(1 for i in range(len(rows) - 1)
                      if float(rows[i + 1]["start"]) >= float(rows[i]["start"]))
        print("\n   %s — %d clips, %d starred, labelled forward on %d/%d steps"
              % (name, len(rows), sum(1 for r in rows if is_star(r)), forward, len(rows) - 1))
        for k, tag in ((2, "video halves "), (3, "video thirds ")):
            buckets = [[0, 0] for _ in range(k)]
            for r in rows:
                b = min(int(float(r["start"]) / duration * k), k - 1)
                buckets[b][1] += 1
                buckets[b][0] += is_star(r)
            print("     star rate by %s %s" % (tag, "  ".join(
                "%d/%d (%.0f%%)" % (s, n, 100 * s / n) if n else "0/0" for s, n in buckets)))
        buckets = [[0, 0] for _ in range(3)]
        for i, r in enumerate(rows):
            b = min(int(i / max(len(rows), 1) * 3), 2)
            buckets[b][1] += 1
            buckets[b][0] += is_star(r)
        print("     star rate by ORDER HE LABELLED  %s" % "  ".join(
            "%d/%d (%.0f%%)" % (s, n, 100 * s / n) if n else "0/0" for s, n in buckets))


def part3():
    print("\n" + "=" * 78)
    print("3. CEILING — an LLM predicting star from Brian's OWN labels, video 2")
    print("=" * 78)
    rows = sorted(fold(RUNS["video2"])[0], key=lambda r: r["start"])
    truth = [1 if is_star(r) else 0 for r in rows]
    if len(truth) != len(LLM_SCORES):
        print("   store has moved: %d clips, %d recorded predictions. Skipping."
              % (len(truth), len(LLM_SCORES)))
        return
    pairs = list(zip(LLM_SCORES, truth))
    a = auc(pairs)
    base = sum(truth) / len(truth)
    print("   base rate %d/%d starred (%.0f%%)" % (sum(truth), len(truth), 100 * base))
    print("   LLM-from-label AUC %.3f, permutation p %.3f" % (a, permutation_p(pairs, a)))
    order = sorted(range(len(truth)), key=lambda i: -LLM_SCORES[i])
    for k in (10, 20, 36):
        top = order[:k]
        print("     top %2d by predicted score: %2d starred (%.0f%%) against %.0f%% base"
              % (k, sum(truth[i] for i in top), 100 * sum(truth[i] for i in top) / k, 100 * base))
    print("\n   Confident and wrong, both directions — the error pattern is the finding:")
    for i in order:
        if LLM_SCORES[i] >= 8 and not truth[i]:
            print("     ranked high, NOT starred:  %s" % (rows[i].get("description") or "")[:56])
    for i in reversed(order):
        if LLM_SCORES[i] <= 3 and truth[i]:
            print("     ranked low, STARRED:       %s" % (rows[i].get("description") or "")[:56])


def part4():
    print("\n" + "=" * 78)
    print("4. WHAT star ACTUALLY TRACKS")
    print("=" * 78)
    rows = [r for run_id in RUNS.values() for r in fold(run_id)[0]]
    base = sum(1 for r in rows if is_star(r)) / len(rows)
    print("   %d clips, base star rate %.0f%%\n" % (len(rows), 100 * base))
    tag_n, tag_star = collections.Counter(), collections.Counter()
    for r in rows:
        for t in set(r.get("tags") or []) - {"star"}:
            tag_n[t] += 1
            tag_star[t] += is_star(r)
    print("   %-18s%6s%10s%8s" % ("tag", "n", "starred", "lift"))
    for t, n in tag_n.most_common():
        if n >= 4:
            print("   %-18s%6d%9.0f%%%7.2fx" % (t, n, 100 * tag_star[t] / n, tag_star[t] / n / base))
    word_n, word_star = collections.Counter(), collections.Counter()
    for r in rows:
        for w in set((r.get("description") or "").lower().split()):
            w = w.strip(".,()-:!?")
            if len(w) >= 3:
                word_n[w] += 1
                word_star[w] += is_star(r)
    ranked = sorted(((w, n, word_star[w] / n) for w, n in word_n.items() if n >= 8),
                    key=lambda x: -x[2])
    print("\n   %-18s%6s%10s%8s   (his own label words, n>=8)" % ("word", "n", "starred", "lift"))
    for w, n, rate in ranked[:5] + ranked[-5:]:
        print("   %-18s%6d%9.0f%%%7.2fx" % (w, n, 100 * rate, rate / base))

    print("\n   Silence gaps — the one transcript-visible proxy for someone playing:")
    hit = tot = star_on = star_off = n_on = n_off = 0
    for name, run_id in RUNS.items():
        run = json.loads((STUDIO / "runs" / f"{run_id}.json").read_text(encoding="utf-8"))
        gaps = {c["start"] for c in (run.get("cues") or []) if c.get("gapBefore")}
        rs = fold(run_id)[0]
        tot += len(gaps)
        hit += sum(1 for g in gaps if any(abs(float(r["start"]) - g) < 1 for r in rs))
        for r in rs:
            if float(r["start"]) in gaps:
                n_on += 1
                star_on += is_star(r)
            else:
                n_off += 1
                star_off += is_star(r)
    print("     clip lands on a gap cue:      %3d clips, %.0f%% starred" % (n_on, 100 * star_on / max(n_on, 1)))
    print("     clip lands on an ordinary cue:%3d clips, %.0f%% starred" % (n_off, 100 * star_off / n_off))
    print("     %d gap cues across the corpus, %d ever became a clip (%.0f%%) — R-TAKE-GAP's"
          % (tot, hit, 100 * hit / tot))
    print("     retirement holds.")


if __name__ == "__main__":
    part1()
    part2()
    part3()
    part4()
