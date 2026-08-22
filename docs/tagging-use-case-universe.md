# The tagging universe

*2026-08-22. An exploration of the markets built on the same primitive as the clipper:
expert judgment, pinned to timestamps, compounding into a searchable corpus and a trainable
tagger. Companion to `docs/youtube-clip-marker-prd.md` — that doc says what we're building
for one user; this one asks where the same machine is worth money. Pricing figures are
directional — assembled from public list prices and reported deal sizes, not verified quotes.*

---

## 1. The primitive

Strip the piano out of the studio and what remains is a loop:

> Long-form footage goes in. A human expert pins judgments to timestamps against a
> controlled taxonomy. A model proposes; the human corrects; every correction is stored
> append-only. Over time the model tags like the expert, and the archive becomes queryable.

Two distinct assets fall out of that loop, and they have different buyers:

- **The corpus** — "show me every moment where X happened, across three years of footage."
  Search value grows with archive size. This is a *retention* asset: whoever holds the tagged
  archive owns the account, because leaving means abandoning the archive.
- **The tagger** — the model that learned the house taxonomy. This is a *cost-destruction*
  asset: it converts expert-review hours into review-the-exceptions hours.

The piano instance is the smallest possible version: one expert, a personal taxonomy, a
personal corpus, labor priced at $0/hour. Every market below is the same loop with someone
else's expensive hours and someone else's valuable moments.

One more thing worth naming: `labels.jsonl` is not a implementation detail here. An
append-only stream of human corrections against model proposals *is the training set and the
moat at the same time*. Most incumbents in the markets below have one half — either a manual
tagging tool with no learning loop, or generic AI tags with no house taxonomy. Very few close
the loop. That gap is the recurring wedge in every entry that follows.

## 2. Four questions that price any of these markets

Before the tour, the rubric. These four questions separate a $20/month hobby tool from a
$2M/year enterprise contract, and they're worth internalizing because they transfer to any
"AI + expert judgment" market, not just this one.

1. **Whose hours burn today, and at what rate?** A sales manager runs $80–150/hr loaded. A
   litigation associate bills $300–700/hr. An attending surgeon's review time is effectively
   unbuyable. You cost $0. Automation value ≈ hours spent watching × rate × fraction of the
   job that is watching.
2. **What is a found moment worth?** A deposition clip that impeaches a witness can swing a
   case. A tagged objection-handling moment closes a rep's skill gap worth a deal. A tagged
   practice loop is worth a better Tuesday. Same loop, four orders of magnitude apart.
3. **Is the taxonomy stable and shared?** A model can only learn tags that mean the same
   thing across taggers and across months. Sports play-calls: extremely stable. UX research
   codes: drift constantly. You have already lived this — the five eval channels collapsing
   into each other is taxonomy drift, and it is why the studio enforces vocabulary. Markets
   with stable taxonomies automate well; markets where every project invents new tags stay
   manual forever.
4. **Does the corpus compound?** Some archives appreciate: sports film, voice-of-customer
   history ("when did customers *start* asking for this?"), a fund's accumulated diligence
   calls. Some depreciate: last quarter's sales coaching calls. Compounding corpora create
   switching costs and make you a system of record; depreciating ones make you a tool.

And one meta-variable that governs pricing power and sales motion — **the budget trigger**:

| Trigger | Character | Examples |
|---|---|---|
| Compliance | Must spend. Sticky, hostile procurement, best pricing. | Comms surveillance, contact-center QA, safety |
| Revenue | Want spend. Fast cycles, crowded. | Sales coaching, investor research |
| Quality / coaching | Should spend. Champion-led, budget fragile. | Surgical review, teacher coaching |
| Passion | Fun. Cheap, but distribution can be viral. | Creators, music, amateur sports |

Pricing power runs top to bottom. Fun runs bottom to top. The interesting entries are the
exceptions that score on both — sports film and flight debrief being the standouts.

## 3. The map

### Cluster A — Revenue-attached conversation intelligence

#### A1. Sales call coaching / revenue intelligence

- **Use case:** Every customer call recorded and transcribed. Managers tag coachable moments
  — weak discovery, pricing raised too early, competitor mentions, talk-ratio violations.
  Reps search their own calls and top-performer calls. Deal risk inferred from what was and
  wasn't said.
- **Industry:** B2B SaaS sales, spreading to every revenue org.
- **Power user:** The frontline sales manager with eight reps, for whom recordings replaced
  ride-alongs; sales enablement builds the taxonomy (Gong calls them "trackers").
- **Budget owner:** VP Sales / CRO — the tools line next to the CRM.
- **Pricing potential:** The proven ceiling of this whole universe. Gong lists around
  $1,200–1,600/seat/yr plus platform fees; mid-market deals commonly land $30k–100k/yr,
  enterprise into high six figures.
- **Current → future:** Today, trackers are keyword-ish and generic; coaching still means a
  manager scrubbing calls, so each rep gets 1–2 calls coached per month and everything else
  goes unwatched; the AI's tags aren't *the team's* tags, so nobody trusts the scorecards.
  Future: manager corrections train a team-specific tagger; scorecards the team believes;
  every call coached, humans on exceptions.
- **Competitors:** Gong, Chorus (ZoomInfo), Clari Copilot, Salesloft, Attention, Fathom and
  Grain at the cheap end, plus every CRM's built-in AI. The most crowded market on this map —
  enter only with an angle the incumbents structurally ignore.

#### A2. Voice-of-customer product signal from sales & support calls

*(The one you named — worth its own entry, because it is not A1.)*

- **Use case:** The calls already happen — sales demos, CS check-ins, support tickets with
  recordings. Product asks, complaints, confusion, and competitor mentions live inside them
  and die there. Tag them at the *moment* level, route to product; over time the corpus
  answers "how often, since when, from which segment," with a supercut as evidence.
- **Industry:** B2B software, seed through growth; any company with a CS org.
- **Power user:** A PM or founder doing discovery; at larger companies, a VoC/insights
  analyst.
- **Budget owner:** Head of Product / CPO — notably *not* the CRO. This is precisely why
  Gong underserves it: the buyer who pays Gong doesn't care about product signal, and Gong's
  roadmap follows its buyer.
- **Pricing potential:** $500–2,000/mo for startups; $30k–100k/yr mid-market as "product
  insight infrastructure." Lower ceiling than A1, far less crowded for the
  timestamped-moment version (text-feedback aggregation is crowded; call-moment mining is
  not).
- **Current → future:** Today, PMs skim recordings only when a roadmap fight breaks out;
  feedback reaches product as secondhand Slack paraphrase; nobody can say whether a request
  is three customers or thirty. Future: every product-relevant moment tagged in a stable,
  PM-curated taxonomy; roadmap debates settled with a search query and a two-minute reel of
  customers saying the thing.
- **Competitors:** Enterpret, Productboard, Canny (all text-centric), Dovetail (adjacent),
  assorted AI-VoC startups — and Gong itself as the distribution threat if it ever decides
  to serve PMs. The corpus compounds hard here: VoC history appreciates.

#### A3. Investor call libraries (expert networks & diligence)

- **Use case:** PE/HF/VC analysts consume expert-network calls and management meetings; tag
  thesis moments — churn signal, pricing power, channel checks. The firm-wide corpus becomes
  proprietary research memory: "everything we've heard about company X's gross margins since
  2024."
- **Industry:** Investment management.
- **Power user:** The analyst listening at 2× with fragmented personal notes.
- **Budget owner:** Head of research / fund COO, out of the data budget — the budget line
  that already pays Bloomberg.
- **Pricing potential:** This buyer pays the highest per-seat rates in SaaS —
  AlphaSense/Tegus-class products historically run $10k–25k+/seat/yr. Even a niche tool at
  $5k/seat clears the bar.
- **Current → future:** Transcripts are keyword-searchable (that is AlphaSense's whole
  business), but the *judgment layer* — what the analyst concluded at that moment — lives in
  personal notes, and when the analyst leaves, the firm's memory walks out with them.
  Future: judgment pinned to moments in a house taxonomy; a compounding house view.
- **Competitors:** AlphaSense (which acquired Tegus), Third Bridge, Stream, Hebbia
  (documents), in-house notebooks. Compliance review is annoying but the money is real.

### Cluster B — Compliance & QA (must-spend)

#### B1. Contact-center QA

- **Use case:** Score 100% of support calls against a QA rubric — greeting, compliance
  disclosure, empathy, resolution. Today humans sample 1–2% of calls. The tagger learns the
  rubric; humans review exceptions and calibrate.
- **Industry:** BPOs, telcos, banks, insurers, healthcare payers — anyone with 200+ agents.
- **Power user:** The QA analyst who listens to calls all day filling scorecards; team leads
  coach from the results.
- **Budget owner:** VP Customer Experience / contact-center ops; sometimes compliance.
- **Pricing potential:** $40–150/agent/mo; thousand-agent centers produce $0.5–2M/yr deals.
- **Current → future:** Sample-based QA misses 98% of calls; agents game known sampling
  windows; scorecard disputes burn calibration meetings. The future state is furthest along
  here already — incumbents genuinely do learn rubrics — so differentiation is thin. Enter
  only through an underserved vertical or geography.
- **Competitors:** Observe.AI, Level AI, MaestroQA, CallMiner, NICE CXone, Verint, AWS
  Contact Lens.

#### B2. Communications surveillance (financial services)

- **Use case:** Regulators require monitoring of trader and advisor communications; flag
  market abuse, complaints, mis-selling in voice. Compliance analysts review flags — a
  tagging loop where false-positive burden *is* the entire cost center (99%+ FP rates are
  normal).
- **Industry / personas:** Banks and broker-dealers; power user is the surveillance analyst,
  budget owner the Chief Compliance Officer.
- **Pricing potential:** Seven figures at global banks. The most lucrative, least fun
  quadrant on the map.
- **Competitors:** NICE, Behavox, Smarsh, Global Relay, SteelEye. Enter only if you love
  procurement, audits, and two-year sales cycles.

#### B3. Industrial safety video

- **Use case:** Sites already run CCTV nobody watches. Tag unsafe acts — missing PPE,
  forklift near-misses, lockout violations; EHS reviews exceptions; the corpus proves safety
  culture to insurers, who sometimes fund the purchase through premium reductions.
- **Personas:** EHS manager (power user); VP Ops / risk (budget).
- **Pricing potential:** Per-site annual contracts, reportedly ~$20–60k/site at the AI
  incumbents.
- **Competitors:** Intenseye, Voxel, Protex AI. Note the different center of gravity: this is
  computer vision on cameras, not conversation on transcripts.

### Cluster C — Expert-skill coaching (the piano pattern at professional stakes)

*This cluster IS your use case — a skilled performance on video, an expert whose attention is
the scarcest resource in the system, a stable pedagogical taxonomy — with someone else
paying.*

#### C1. Surgical video review

- **Use case:** Laparoscopic and robotic surgery is recorded by default. Tag procedure
  phases, critical-view moments, errors, idle time. Residents get timestamped feedback;
  departments benchmark technique against outcomes.
- **Industry:** Hospitals, residency programs, and device makers (who fund studies).
- **Power user:** The surgical resident, starving for feedback, and the program director.
- **Budget owner:** Hospital quality/education budgets; device-maker sponsorships (often the
  bigger check); GME programs.
- **Pricing potential:** Six-figure hospital contracts; device-company partnerships larger.
- **Current → future:** Attendings have no time to review footage; feedback is verbal in the
  OR and evaporates; formal skill assessment (OSATS-style) is manual and rare. Future: the
  model pre-tags phases and candidate moments, the attending corrects in minutes — exactly
  the suggest→correct loop, with the correction cost pushed onto the cheap side of the
  expert's attention. Barriers: PHI, IRBs, and the med-legal fear that recorded error is
  discoverable.
- **Competitors:** Theator, C-SATS (J&J), Proximie, Touch Surgery (Medtronic). Slow cycles,
  deep moats once in.

#### C2. Sports film breakdown — the fun-and-lucrative flagship

- **Use case:** Every level of organized sport tags game film: play type, formation,
  personnel, outcome. High-school coaches do it by hand on Sunday nights; college programs
  employ video coordinators; pro teams run analyst rooms.
- **Industry:** Team sports at every level. Hudl proved that *even high schools* pay.
- **Power user:** The video coordinator / assistant coach who loses every Sunday to tagging
  Saturday's game.
- **Budget owner:** Athletic director (school), club treasurer, or the head coach's budget
  line.
- **Pricing potential:** Hudl's high-school tiers run roughly $400–3,500/team/yr; college
  and pro tooling reaches tens of thousands per program. Hudl is a ~$400M-revenue company —
  the existence proof that timestamp-tagging alone can be a real industry.
- **Current → future:** Hudl Assist outsources tagging to humans with turnaround delay;
  Sportscode is powerful but manual. Future: the model learns *the program's own* tagging
  scheme, the coordinator corrects, breakdown is done by midnight. The catch: Hudl's moat is
  not tagging, it's the film-exchange network between schools — you don't beat that head-on.
- **Competitors:** Hudl (plus its Sportscode, Wyscout, Volleymetrics properties), Catapult,
  Dartfish, Synergy Sports, sport-specific AI startups. The open doors are niche sports the
  giants ignore, and the tagging-automation layer sold *into* Hudl's world rather than
  against it.

#### C3. Teacher & classroom coaching

- **Use case:** Recorded lessons tagged against instructional rubrics — questioning
  technique, wait time, student engagement. Instructional coaches leave timestamped comments;
  districts run professional development on real footage instead of role-play.
- **Personas:** Instructional coach (power user); district PD budget, often US Title II
  funds (budget owner).
- **Pricing potential:** $100–300/teacher/yr; district deals $20k–200k. Procurement is slow
  and grant-dependent — the budget trigger is "should," which makes it fragile.
- **Competitors:** Edthena, TORSH Talent, TeachFX (audio analytics), GoReact, Swivl.

#### C4. Therapy & clinical-conversation fidelity

- **Use case:** Tag therapy sessions for technique fidelity — motivational-interviewing
  adherence, CBT technique use. Supervisors coach from moments; payers are beginning to
  demand quality evidence for behavioral health.
- **Personas:** Clinical supervisor (power user); training clinics, behavioral-health
  chains, and increasingly payers (budget).
- **Pricing potential:** Per-clinician SaaS, growing as measurement-based care gets teeth.
- **Competitors:** Lyssn (the reference player), Eleos Health, Blueprint. PHI-heavy, but the
  taxonomy (therapy fidelity codes) is unusually stable — academically standardized — which
  is exactly what question 3 rewards.

#### C5. Flight & mission debrief — the exotic one

- **Use case:** Military and airline training sorties produce cockpit, HUD, and simulator
  footage. Instructor pilots prepare debriefs by scrubbing tape; tag maneuvers, deviations,
  comms errors; squadrons trend weaknesses across classes.
- **Personas:** The instructor pilot, whose debrief prep eats hours per sortie (power user);
  training command / defense procurement, or an airline's AQP training department (budget).
- **Pricing potential:** Defense contracts — six to eight figures, with a brutal sales cycle
  and primes as required partners.
- **Competitors:** CAE and the sim vendors' own tooling, a scatter of defense-tech startups,
  and a vast incumbent installed base of duct tape and PowerPoint. Fun score: maximum.

### Cluster D — Research & legal insight repositories

#### D1. UX research repository

- **Use case:** User interviews and usability sessions tagged into an insight taxonomy; the
  repository answers "what do we know about onboarding friction?" across two years of
  studies instead of re-running the study.
- **Personas:** UX researcher (power user); ResearchOps runs the repository; Head of
  Design/Research pays.
- **Pricing potential:** $30–100/user/mo; org deals $20k–150k/yr.
- **Current → future:** Manual tagging is Dovetail's number-one complaint; taxonomies rot
  ("repository graveyard" is a ResearchOps meme); insights get re-discovered quarterly.
  Future: the model learns the house codebook, the researcher corrects, the repository stays
  alive. Context: research headcount was cut hard 2023–2025 — which is exactly when
  "automate the tagging" resonates. But note question 3: insight taxonomies drift by
  design, which caps how far the tagger generalizes.
- **Competitors:** Dovetail, Marvin, Condens, Looppanel, Notably, Grain, UserTesting.

#### D2. Depositions & trial prep

- **Use case:** Deposition video synced to transcript. Associates designate testimony
  clips, tag by issue and impeachment potential; the trial team assembles clip reels;
  opposing designations get compared and countered.
- **Personas:** Litigation paralegal / junior associate (power user); the partner, billing
  it to the client, or a lit-support director (budget). Insurance defense brings volume.
- **Pricing potential:** Legal pays per matter — $5k–50k/matter for video work is
  unremarkable, and the hours being replaced bill at $300–700. The highest hourly rates on
  this map are doing the watching.
- **Current → future:** Designations are exchanged in Excel as page:line cites; a human
  re-cuts video to match; issue tags get rebuilt for every case because taxonomies are
  case-specific. That last point is the catch — question 3 scores *low across cases*, high
  within one, so the learning loop resets per matter. The corpus compounds per-firm only for
  recurring litigation types.
- **Competitors:** Opus 2, Everlaw, Relativity (adjacent), TrialPad, and the court-reporting
  vendors (Veritext) bundling video sync.

#### D3. Qualitative market research / focus groups

- **Use case:** Focus groups and in-depth interviews for CPG and pharma, tagged for
  reactions and themes; the highlight reel *is* the client deliverable.
- **Personas:** Qual researcher at an insights agency (power user); brand insights director
  (budget — and research budgets are real: $50k–500k study programs).
- **Competitors:** Discuss, Forsta, Voxpopme, and the agency's own interns.

### Cluster E — Media & creative (high volume, taste-driven)

#### E1. Broadcast & archive logging

- **Use case:** Newsrooms and sports broadcasters log footage — who, what, event, rights
  status. Loggers tag live; archives are monetized through licensing and re-use, and an
  unsearchable archive is dead inventory.
- **Personas:** Media logger / archivist / producer (power user); head of post-production or
  archive director (budget).
- **Pricing potential:** Media asset management systems run $50k–500k+; logging tools ride
  on top per-seat.
- **Current → future:** Generic AI tagging (faces, objects, shot types) already exists — but
  the *editorial* taxonomy ("great save," "controversial call," "usable pull-quote") is
  house-specific. Same wedge as everywhere: generic AI without house taxonomy. The looming
  factor: video foundation models commoditize the generic layer fast.
- **Competitors:** Iconik, Dalet, Avid, Moments Lab, Twelve Labs, Reduct.video.

#### E2. Creator clipping — the cautionary entry

Opus Clip, Descript, Eklipse and a dozen others turn streams into shorts at $15–30/mo.
Model-picks-the-moments is already a commodity; churn is brutal; there is no taxonomy and no
compounding archive — which, per questions 3 and 4, makes it a feature market, not a corpus
market. Fun, but skip it except as top-of-funnel.

### Cluster F — Passion & long tail (quick hits)

- **Music practice & masterclass indexing** — home base. Tonebase-style catalogs, lesson
  marketplaces, conservatories. Small dollars, real love, near-greenfield for the tagging
  loop.
- **Esports scrim review** — pro orgs employ analysts who tag VODs; fun ceiling very high,
  budgets thin outside the top orgs.
- **Oral history & archives** — museums, universities, StoryCorps-adjacent. Grant-funded,
  mission-driven.
- **Field research footage** — camera traps, marine video; Zooniverse crowdsources exactly
  this loop. Joyful, unfunded.
- **Sermon & conference repurposing** — churches clip weekly long-form video on a deadline;
  a surprisingly real niche-SaaS market.
- **Robotics / AV data curation** — the industrial cousin: expert-in-the-loop tagging of
  fleet video to train perception models (Scale AI, Encord, V7, Labelbox). Lucrative, but
  it's a different product shape — labeling ops, not a workspace.

## 4. The pattern — what's actually defensible

Generic video understanding is commoditizing fast; foundation models will tag "person plays
arpeggio" or "customer sounds frustrated" for pennies. What they cannot ship is:

1. **The private taxonomy** — work/lane/tags that mean something to *this* team;
2. **The correction history** — the append-only record of expert disagreement with the
   model, which is simultaneously the training set and the audit trail;
3. **The workflow** — keyboard-first review that makes corrections cheap enough that experts
   actually produce them;
4. **The archive gravity** — the compounding corpus that makes leaving expensive.

That stack is, item for item, what the studio already is: the taxonomy discipline,
`labels.jsonl`, the keyboard grid, the run store. The incumbents in nearly every cluster
above have either a manual tagging tool with no learning loop, or generic AI with no house
taxonomy. Closing the loop is the recurring, structural wedge.

## 5. If I were choosing

Scored against the four questions, a shortlist:

1. **VoC product-signal for startups (A2) — the fast wedge.** Buyers you can reach this
   month, recordings that already exist behind Gong/Zoom/Fathom APIs, a small stable
   PM-curated taxonomy, incumbents structurally pointed at a different buyer, and a corpus
   that appreciates. Moderate ceiling, fastest path to a first paying customer.
2. **A niche-sport film vertical (C2) — the fun wedge.** Proven willingness to pay at every
   level, joyful users, maximum taxonomy stability. Pick a sport where footage exists and
   Hudl Assist doesn't reach, and sell the Sunday night back to the coach.
3. **Expert-skill coaching (C1/C4/C5) — the long game.** Surgical, clinical, and flight
   debrief have the deepest moats and the best stories, but each is a multi-year regulated
   grind. Enter later, or through partners who already hold the compliance keys.

And the reframe worth keeping: piano is not the lowest-value use case — it is the
**zero-cost laboratory**. It is where the loop, the taxonomy discipline, and the eval harness
get built with an expert user (you) whose corrections are free and whose patience is
infinite. Hudl started as Nebraska football's internal tool. The studio plus `labels.jsonl`
plus the eval loop is the R&D rig for every row in the table below; each market is that rig
plus a skin plus a distribution problem — and distribution, not technology, is the hard part
in all of them.

## 6. Summary table

| Use case | Trigger | Deal size (order of magnitude) | Taxonomy stability | Corpus compounds? | Crowding | Fun |
|---|---|---|---|---|---|---|
| Sales coaching (A1) | Revenue | $30k–500k/yr | Medium | Weakly | Severe | ○○ |
| VoC product signal (A2) | Revenue | $6k–100k/yr | High | Yes | Light | ●○ |
| Investor libraries (A3) | Revenue | $5k–25k/seat/yr | Medium | Yes | Medium | ●○ |
| Contact-center QA (B1) | Compliance | $0.5–2M/yr | High | Weakly | Severe | ○○ |
| Comms surveillance (B2) | Compliance | $1M+/yr | High | Yes (audit) | High | ○○ |
| Safety video (B3) | Compliance | $20–60k/site/yr | High | Yes (audit) | Medium | ○○ |
| Surgical review (C1) | Quality | $100k+/hospital | High | Yes | Light | ●● |
| Sports film (C2) | Passion+Quality | $0.4k–35k/team/yr | Very high | Yes | Hudl | ●● |
| Teacher coaching (C3) | Quality | $20–200k/district | Medium | Weakly | Medium | ●○ |
| Therapy fidelity (C4) | Quality | per-clinician SaaS | Very high | Yes | Light | ●○ |
| Flight debrief (C5) | Quality | $1M+ contracts | Very high | Yes | Light | ●● |
| UX repository (D1) | Quality | $20–150k/yr | Low (drifts) | Meant to | High | ●○ |
| Depositions (D2) | Revenue (billable) | $5–50k/matter | Low across cases | Per-firm | Medium | ●○ |
| Qual research (D3) | Revenue | per-study | Medium | Per-brand | Medium | ●○ |
| Broadcast logging (E1) | Revenue | $50–500k | Medium | Yes | Medium+FMs | ●○ |
| Creator clipping (E2) | Passion | $15–30/mo | None | No | Severe | ●● |
| Music / masterclass (F) | Passion | small | High | Yes | Greenfield | ●● |
