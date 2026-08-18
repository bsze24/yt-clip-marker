# Agent coordination

The async handoff surface between Brian and whatever agents are working this repo. Git is
the source of truth for **code**; these files are the source of truth for **intent** — what
is being built now, what was decided, what is deliberately parked.

Agents here do not run continuously and do not share context. A turn ends, and the next one starts cold, possibly in a different product. Everything the next turn needs must be written down before this one stops.

The core rule that follows:
**The baton names a role, not a product.** `→ reviewer`, never `→ Codex`. Which model sits in a role changes turn to turn; the handoff note records which one it actually was.


## Files

| File | Holds |
| --- | --- |
| `CURRENT.md` | The one active task: scope, acceptance criteria, verification, baton. |
| `REVIEW.md` | The active review target(s); findings as per-item threads with a status. |
| `BACKLOG.md` | Roadmap, deferred work, tech debt (`TD-N`), open modeling decisions. |
| `DECISIONS.md` | Durable architecture and product calls (`D-001`…). |

**On `DECISIONS.md`.** Other files should cite durable calls as `[[D-xxx]]`. Those ids are the contract; do not relitigate a decision silently. If you think you should do so, please flag it before acting.

If the file is missing from the tree you are standing in, resolve the citation against git rather than inferring the decision from
the id alone:

```bash
git log --all -- docs/coordination/DECISIONS.md
```

## Shared vocabulary

Three kinds of **marker** share the grid. The product names are parallel; the store is not —
they are three records, not three values of one `type` field. Use these words exactly:

| Word | What it is | Store |
| --- | --- | --- |
| **skill marker** | Proposed by the `yt-clipper` skill | `runs/{id}.json` `markers[]`; identity `markerIndex` |
| **added marker** | Created by a human in the studio after ingest | `labels.jsonl` as `miss` / `unmiss`; identity `(runId, start)` |
| **extracted marker** | Parsed from the published YouTube description | `run.extracted[]`. A `gold[]` key is a visible load fault, not an alias. No label events. |

`g` and `x` grade **skill markers** only. The same `x` *key* on an added marker deletes it
(writes `unmiss` — leftover eval slang for the delete button). Do not say **gold** for an
extracted marker; that word collides with the `g` few-shot grade.

The eval verdicts are five distinct channels and must not be collapsed into "keep vs skip":

- `g` — few-shot exemplar of a **skill marker**. Stingy. This is the positive training signal.
- `x` — reject this skill marker. The negative signal. The same key on an *added marker* deletes it.
- taxonomy (work / lane / tags) with no `g` — an ordinary keep, not a blank.
- `star` — Brian's personal bookmark. A tag, not eval.
- blank feedback and no taxonomy — genuinely unreviewed.

**The standing trap: displayed time is not stored identity.**

Every grid row is a caption, and the left column is when that caption started. A clip record
carries its own time in the store. When the two match exactly the record sits on that caption's
row and both numbers agree. When they do not match, the grid still has to place it, so it uses
the nearest caption within 2 seconds — and the row then shows the *caption's* time while the
record's own time appears nowhere on screen. The code calls this being *aligned onto* a cue.

Measured on video 1, 2026-08-18:

- **Extracted stamps are where this happens** — 19 of 24. A human typed them into the YouTube
  description while watching, and people type round times while captions begin whenever someone
  starts talking. `Tricky F alt lick fingering` is stored at `280.0` (`4:40`); no caption starts
  at 280, the nearest are 278 and 279, so it renders on the `4:39` row. Export writes `4:40`.
- **Skill markers never do** — 0 of 64. The suggester is only ever shown the caption list, one
  timestamp per caption block, so whatever it proposes is already a caption time.
- **Added markers never do** — you create them with Enter on a grid row, so they inherit that
  row's caption time by construction.
- **Labels cross records.** An extracted stamp within 2s also wins the row's label, so the text
  you read can belong to a record stored at a different second than the time beside it. At
  `1:18:57` the added marker stored at `4737` displays "Freedom Demo c1" — the label of the
  extracted stamp stored at `4738`.

The earlier version of this paragraph said skill marker 53 stored at `1:18:52` displays at
`1:18:50`. That was true under earliest-cue-wins and stopped being true when [[D-008]] made
alignment exact-start-first; there is a cue at exactly `4732` and marker 53 sits on it. It also
cited an added marker at `1:18:54` that has been tombstoned since 2026-08-16. Both claims
misled a reviewer on 2026-08-18. Do not restore them.

Before arguing about a timestamp, dump the stored identity — `markerIndex` for a skill marker,
`start` for an added marker — and check `labels.jsonl` for an `unmiss` before concluding a
record is missing.

## Roles

Stable roles, rotating occupants. The table says who usually holds each; the baton and the
handoff note are authoritative for any given turn.

| Role | Owns | Usually |
| --- | --- | --- |
| Planner | Design, `DECISIONS.md`, writing the `CURRENT.md` spec | Claude Code |
| Implementer | Code for the active task; the commit SHA and its verification | Codex or Cursor |
| Reviewer | `REVIEW.md` findings; may implement when explicitly assigned | Claude Code |
| Owner | Product and scope calls; invokes each turn; breaks ties | Brian |

Neither implementer nor reviewer may revise a decision. If the task cannot be built as
specced without contradicting one, it goes back to the planner (design and contract) or to
Brian (product and scope).

## Working agreement

1. **One active task in `CURRENT.md`.** A genuine second thing is either part of the same
   task or belongs in `BACKLOG.md`.
2. **Cite an exact SHA** when requesting or recording a review, and verify it is on the
   branch before acting: `git merge-base --is-ancestor <sha> HEAD`.
3. **Label every finding blocking or optional.** Optional findings never hold a baton.
4. **Thread each finding in place** — finding, response, re-review, one item, one status. No
   separate "responses" section.
5. **Never `git add -A`.** Run data (`runs/`, `labels.jsonl`) and session logs are not the
   product PR. Coordination docs travel with product docs, not with a video's labels.
6. **Graduate to GitHub issues** if this outgrows four files. It has not yet.

## Handoff cycle

1. **Planner** specs the task in `CURRENT.md`.
2. **Brian** resolves any product or scope choice the spec surfaced.
3. **Implementer** builds it, then records the SHA and its verification in `CURRENT.md`.
4. **Review loop** — implementer and reviewer iterate until no blocking finding remains.
5. **Planner** scopes the next task once review lands clean.

Brian invokes every turn. Brian or the planner break ties.

### Before recording a SHA (step 3, expanded)

Cheap obligations that keep review to one or two rounds instead of five.

**1. Audit the work against `CURRENT.md`.** Write all three parts into the handoff note
before recording the SHA:

- **Acceptance criteria, one at a time.** Cite the evidence — function, file, line — or say
  plainly what is missing. "Done" with no pointer is not verifiable.
- **Assumptions.** Wherever the spec left two reasonable implementations open and you picked
  one, name the choice and why. A reviewer cannot tell a deliberate interpretation from an
  oversight unless you say which it was.
- **Skips and divergences.** Anything not built, or built differently. Cutting scope is
  Brian's call, so surface it rather than absorb it.

The same three-part audit applies to any session driven by a prompt file, before commit.

**2. Run the checks that exist — and know which ones you cannot run.** There is no test
suite, no typecheck, no build step. What is verifiable depends on what you are:

*Any agent, from the shell:*

```bash
python3 apps/studio/server.py            # from the repo root; serves 127.0.0.1:8765
curl -s http://127.0.0.1:8765/ | head
curl -s http://127.0.0.1:8765/api/runs
curl -s "http://127.0.0.1:8765/api/run?id=YYW4Q1Nivg8-20260814-1248" | head -c 500
```

`index.html` is served from disk on every `GET /`, so HTML and `ui/*.js` edits show on
refresh. Changing `server.py` needs the process restarted. If 8765 answers empty, it is
probably a zombie `eval/server.py` — that folder is a husk, kill it first:

```bash
lsof -nP -iTCP:8765 -sTCP:LISTEN
```

*Only a human, or an agent driving a real browser:* the annotation loop itself. Grid
rendering, `j`/`k` selection, Enter to add, focus returning from the YouTube embed, the
copy-timestamps output, and whether the extension loads unpacked with a clean console on a
watch page. **Having the source files is not having the tab.** An agent that reads
`grid.js` and curls `/api/run` has verified the data path and nothing about the interaction.

Say which half you did. Claiming a keyboard behaviour works when you only read the
dispatcher is worse than recording that you could not check it — write "not verified, needs
a browser" and let the finding stand open.

Paste what you actually did into `CURRENT.md`. "It works" is not evidence.

**3. Scan the diff for what this codebase has actually got wrong:**

- Missing try/catch around async work — `fetch` in the studio page, `chrome.*` APIs.
- Missing empty and error states — no runs, ingest failure, absent `<video>` element, a save
  that fails silently.
- Edge cases: empty `markers[]`, null `videoId`, null `end`, two rows sharing a start time,
  a stop with no pending start.
- Unguarded keyboard listeners: input focus, modifier keys, `e.repeat`, IME composition. In
  the extension the focus check reads `e.composedPath()[0]`, because `document.activeElement`
  cannot see through a shadow root. In the studio, check that focus returns from the player
  iframe — otherwise the next keystroke goes to YouTube instead of the grid.
- Row identity over start time anywhere selection or alignment is involved.
- Secrets. No keys or tokens in committed code.
- When you fix a bug, check the same file for the same mistake elsewhere.

**4. Batch related fixes** into one commit rather than a chain of one-line follow-ups. Do not
push while BugBot is mid-review — the review restarts.

**5. Do not silently revise a decision.** See Roles.

### The review loop (step 4, expanded)

Not one pass. A short back-and-forth that repeats until no blocking finding is open.

1. **Reviewer** reviews the cited SHA, writes each finding as its own item in `REVIEW.md`:
   severity, status `open`.
2. **Implementer** answers inline under each finding — fixed, or `wontfix` with a reason —
   cites the new SHA, flips that item to `addressed`.
3. **Reviewer** re-reviews at the new SHA, writes the verdict under the item, sets `resolved`
   or returns it to `open`.
4. Repeat 2–3 until zero blocking findings are open. Optional items get `deferred` into
   `BACKLOG.md` rather than holding the handoff.
5. **Brian or the planner** breaks any stalemate — Brian on product and scope, the planner on
   design and contract.

Status ladder: `open → addressed → resolved`, or `deferred` / `wontfix`. Findings are
append-only: add underneath, never rewrite the original text. With several targets in flight,
use one `## Thread` per SHA and edit only the thread whose baton you hold.

**Severity is measured, not asserted.** Where a real store exists — a run file, `labels.jsonl`,
a committed dataset — check whether the finding actually fires on it *before* setting severity,
and put the result in the finding. `blocking` means it costs Brian something concrete on data
that exists today. A defect the code permits but the data never triggers is still real and still
worth fixing; it is not blocking. Say which, and say how you know.

This is not hypothetical. F7 was filed `blocking` on the strength of what `mergeNearby` could do,
demonstrated with a constructed input. On video 1 it never fired once — the drift needs a chain
of three clips inside the fold window and there are zero such chains. The check took two minutes
and the data was available at filing time. The cost was a round trip and a reviewer's report that
read far more alarming than the code deserved.

**Say what a finding would actually cost.** Of fifteen findings on PR 3, three would have cost
Brian something he would notice: a broken chapter list, silently dropped annotation edits, and a
saved lane reverting on the next keystroke. The rest were latent, cosmetic, deferred or
`wontfix`. "Fifteen findings, three blocking" and "three that would bite you, twelve for the
record" describe the same review and set opposite expectations. Write the second one.

### Wrap-up (when review lands clean)

`REVIEW.md` is live state, not an archive. Git history and the PR thread already hold the
round-by-round.

1. **Harvest.** Anything durable becomes a dated `DECISIONS.md` entry; anything deferred
   becomes a `BACKLOG.md` item. The discussion itself is not kept.
2. **Reset `REVIEW.md`** to a clean ledger pointing at the next target, or "no active review".
3. **Planner** replaces `CURRENT.md` with the next spec.

No per-PR archive files. `docs/prs/pr-*.md` are the task specs that became PRs — provenance,
not a second `CURRENT.md`.

## Where things go

| Kind | Home |
| --- | --- |
| Active task, baton, acceptance | `CURRENT.md` |
| Review findings | `REVIEW.md` |
| Roadmap, deferred work, tech debt | `BACKLOG.md` |
| Durable architecture and product calls | `DECISIONS.md` |
| Product requirements — the why | `docs/youtube-clip-marker-prd.md` |
| Clip contract | `docs/clip-schema.md` (PR 3) |
| Session and learning state | `docs/sessions/`, one file per session |
| A video's labelled state, folded for reading | `docs/sessions/<date>-<videoId>-folded-ledger.md` |
| Two-surface pivot provenance | `docs/two-surface-handoff.md` — historical, not live |

**Finding the right session log.** Filter by `track:`, then read the file's own "Project
context" block to find which one is the resume head. Do not take the newest match. On
`track: studio-workspace` the newest file is `2026-08-17-1740-grok-studio-prototype-handoff.md`,
and it says in its own first lines that the head is
`2026-08-16-1507-grok-studio-fable-lock.md`. Filenames carry the date the log was *written*,
not the dates it covers, so recency ordering lies whenever a log is written after the fact.

A real project finding that surfaces during a learning session — a bug, a contract gap — is
project state and routes here. What the artifact is decides its home, not how it came up.
