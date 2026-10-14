# Threading, time zones, and dedup — analysis and planned features

Reference doc for the next phase of work on the email parsers (po-emails,
farrar-fauci). Written before starting so the reasoning is on record, not just
the code. Builds on `SPEC.md` (the data model) and the shared `foia_parser`
package's `SKILL.md` (the general FOIA-email-parsing lessons) — read those
first if the vocabulary here is unfamiliar (`recovered_inline`, `thread_key`,
`stamp_status`, etc.).

---

## 1. Where this picks up

Both email parsers were extracted into a shared library,
`~/Work/Edition/foia_parser/`, so a fix in one release's grammar now reaches
both. That extraction surfaced three real, pre-existing bugs (all now fixed
and verified — 73/66/33 tests, zero chronology violations in either corpus):

1. `strip_quoted()` treated "Thanks," / "Many thanks" as a sign-off trigger
   with no length guard, so genuine prose opening with either phrase ("Thanks,
   Jeremy. Great chatting with you and Patrick...") had its entire body wiped.
2. The inline quote marker (`On <date>, <name> wrote:`) didn't tolerate a
   leading `>` (a blockquoted marker), so that nested reply was never
   recovered as its own entry.
3. The *synthesized* `Sent:` line for a recovered inline message used a
   comma between date and time ("Feb 5, 2020, 7:20 AM"), which broke every
   stamp-parsing regex and silently discarded the real time in favour of a
   noon default. This alone caused `merge_page_splits()` to wrongly collapse
   dozens of genuinely distinct undated messages into single garbled entries
   (po-emails went from 161 → 227 entries once fixed).

Also added: recovered-inline messages now get an **explicit** `reply_to`
link to the message that quotes them (not dependent on subject-matching,
which could never work for them — they never carry a subject), guarded so
it's only asserted when chronologically consistent; a `[NA]` placeholder
where a field couldn't be recovered, instead of leaving it blank; and
clickable links for any URL in a box's text (UI-side `linkifyUrls()`, plus a
narrow parser-side `harden_urls()` that undoes one verified OCR artifact — a
long digit run, e.g. a PubMed ID, split by a stray inserted space).

None of that is enough on its own, though — it fixes individual messages,
not the *shape* of the corpus. Three problems remain, in dependency order.

## 2. The time-zone problem: a quoted stamp is frozen in the REPLIER's zone

**Status: built for the explicit-link case and the GARRY page-owner code;
REV's actual zone is still an open question (see below) — left deliberately
unresolved rather than guessed at.**

This is the one that has to be fixed first, because dedup and the thread
panel both build on `date`/`time` being right.

**The mechanism** (verbatim, from the user's own P.O. piece — this is the
load-bearing insight for everything below):

> When the FOIA emails are a clear thread made of consecutive replies, the
> best is to read them backward, starting from the last one, while noting
> that the timezone of each email is often the one of the person replying
> directly to the email, not of the person who wrote the email.
>
> Indeed, each reply may freeze the time of the replied-to email in the
> time-zone of the person replying directly. This is due to the fact that,
> when an email is replied to, a simple email client would typically take
> the 'sent' time of the replied-to email in the time-zone of the person
> replying, and dump it as text in the new email. From there, that text
> becomes immutable and just gets included with each further reply-to as
> any other text.
>
> When the last email in the thread is not one that somebody replied to,
> which can often be seen from the pagination, the code in the bottom-right
> corner of the page typically gives the owner of the mailbox, which then
> gives the time zone of that email (i.e.: LIPXXXX refers to Lipkin's email
> box). However, some threads seem to be partially reproduced, making it
> more difficult to understand the timezone of the apparent last FOI'd email
> in the thread. Of note, REVXXXX, whatever that one is, is UK −8.
>
> Also, pay attention to these YYXXXX codes in the right corner. Some
> Congressional documents are a mash-up of emails extracted from different
> mailboxes (different YYs), and reordered in an approximate chronological
> order. Understanding these user transitions helps identify the continuous
> threads and the timezone of the last email in each thread.

**Why `zone_for()` is wrong today.** The current model picks a zone from the
*sender's own* institutional affiliation (Andersen → Scripps → Pacific,
Farrar → Wellcome → London, etc.) — correct for the outer, top-of-chain
message a sender actually composed, but **wrong for any quoted copy of an
earlier message nested inside a later reply**. That quoted copy's printed
stamp is not evidence of the original sender's zone at all; it's evidence of
whatever the *replier's own mail client* rendered at reply time. Right now
this misattribution hits two kinds of entry, not just inline-marker
recoveries:

- Inline `On <date>, <name> wrote:` markers (handled today, but zoned by the
  *quoted* sender's affiliation — should be zoned by the *quoting* message's
  own zone instead, once that's known).
- Literal nested `From:`/`Date:`/`Sent:` header blocks that appear **inside**
  a later message's body, printed exactly like a top-level header and
  currently segmented as an independent message the same way (see `SPEC.md`
  §2, boundary type 2) — these get the *same* wrong treatment, just via
  `zone_for()`'s normal sender-affiliation path rather than the inline-quote
  path.

**Confirmed in the corpus** (not hypothetical — grepped directly):

- po-emails.pdf carries two distinct bottom-corner stamp families: `REV%07d`
  (108 pages) and `GARRY%07d` (25 pages) — exactly the "different mailboxes
  mashed together" pattern described above. `GARRY` is presumably Robert
  Garry's own mailbox export; `REV` per the user's note is UK (−8 noted, not
  yet reconciled against a plausible UK offset — needs a joint pass over a
  few REV-stamped pages to pin down what "−8" is actually recording).
- farrar-fauci-comms.pdf shows **no** equivalent bottom-corner marker family
  in the same sweep (checked the first several pages' closing lines) — either
  it uses a different convention not yet found, or this release doesn't carry
  one at all (most of its top-level stamps already carry an explicit UTC
  offset, which may be why: less need for the mailbox-owner fallback).

**Built** (`foia_parser/core.py`'s `reconcile_zones()` + `page_owner_map()`,
run as a pass after `merge_page_splits()` and before thread keys are
assigned, so a correction is reflected in the key and in every downstream
chronology check):

1. `Profile.page_owner_re` / `Profile.page_owners`: a regex for the page's
   bottom-corner code, matched against the page's own last non-blank line
   (independent of segmentation — read straight off the raw OCR text), and a
   prefix → `(zone, why)` table. A prefix present with value `None` means
   "recognised, but deliberately left unresolved" (see REV below) rather
   than guessed at.
2. Zone preference order, per message: an explicit UTC offset in its own
   stamp (unchanged, always wins) → the zone of the message that **quotes
   it** (propagated via `segment()`'s `quotes_msg` link — the *explicit*
   inline-quote case only, see the limitation below) → this message's own
   page-owner code, if mapped → the existing sender-affiliation guess
   (unchanged fallback, tried first before this pass and left alone when
   nothing better is found).
3. Quote-chain propagation is a fixed-point iteration (a chain can nest
   several quotes deep: Garry quotes Andersen quotes Garry quotes Holmes,
   a real 4-deep case in po-emails) — a message's zone only propagates to
   what it quotes once its OWN zone is confidently resolved (offset,
   page-owner code, or already-propagated), never from a plain
   sender-affiliation guess.

**Confirmed working** in both corpora (zero chronology violations in
either, verified after every change, deterministic across repeated runs —
see the tie-break fix below): po-emails.json has 147 entries corrected by
REV, 42 by GARRY, 28 by LIP (all page-owner codes), and 10 by quote-chain
propagation; farrar-fauci.json (no page-owner table — none found in that
release) has 2 corrected by propagation alone.

**REV resolved.** Confirmed with the user: unidentified (never traced to a
specific person or office — "I have not ID'd what REV is"), but empirically
US Pacific time, UTC−8 standard / UTC−7 daylight, could be off by up to an
hour. `page_owners["REV"] = ("America/Los_Angeles", ...)` — `ZoneInfo`
handles the standard/daylight switch on its own, so one zone key covers
both. The earlier note ("REV... is UK −8") reflects not knowing WHAT it is,
not that it's in the UK — "UK" there was a placeholder, not a claim about
the code's origin. Still not contiguous (0000750–0000803 *and*
0001890–0002865, with the GARRY run spliced in between) — still evidence
it's some recurring process stamp rather than one person's mailbox export,
just one with a now-known effective zone regardless of what it is.

**A third mailbox code found and resolved**: `LIP-%06d` (17 pages, two short
runs: 472–473 and 615–652) — W. Ian Lipkin's own mailbox export (Columbia
University → America/New_York), exactly the "LIPXXXX → Lipkin's mailbox"
example from the original note. Printed differently from GARRY/REV: glued
onto the tail of a multi-line committee banner ("...MEMBERS AND STAFF ONLY
LIP-000472") rather than standing alone as the whole line, which needed
`page_owner_re` matched with `search()` (the code is always the tail of the
line) rather than `match()` (which required it to BE the whole line).

**A real nondeterminism bug found and fixed along the way**: the page-owner
tie-break (`max(set(owners), key=owners.count)`, for a message spanning a
splice point between two differently-stamped pages) depended on Python's
per-process hash-randomized set iteration order — caught by running the
SAME release twice in separate processes and diffing, which disagreed on
one entry's zone. Fixed to break ties deterministically (earliest-page
occurrence among the tied codes) and reverified deterministic across
repeated fresh-process runs.

farrar-fauci-comms.pdf was checked for an equivalent bottom-corner code
family and none was found (its own top-level stamps mostly carry an
explicit UTC offset already, which may be why one was never needed) — its
`Profile` has no `page_owner_re` configured, and `page_owner_map()` simply
returns `{}` for a profile that doesn't set one.

**Known limitation, not yet addressed**: this only propagates zones through
the *explicit* inline-quote link (`segment()`'s `quotes_msg`). A literal
nested `From:`/`Date:` header block quoted inside a later reply (SPEC.md §2,
boundary type 2) gets no such link today — only the *inferred*,
subject-matching kind (`thread_entries()`), which isn't reliable enough to
drive a zone correction on. Extending this would need a way to tell "this
From: block is a NESTED quote inside the previous message's body" apart from
"this From: block is simply the next independent top-level message in the
print stream" — the two are structurally identical to `segment()` today, and
solving that is its own, separate piece of work.

## 2b. Duplicate body text found and mostly fixed along the way

Spotted via a screenshot of a box showing the same paragraph twice. Three
distinct, now-understood causes, two fixed:

1. **`merge_page_splits()`'s dedup check compared a whole blob, not a
   prefix.** The release prints the same real email in more than one
   mailbox's own export, each OCR'd independently (confirmed: "Lj External
   Sender..." in one copy, "(J External Sender..." in the other — the same
   glyph misread two different ways), which defeated an exact substring
   check. Worse, when the LATER copy also had something genuinely new glued
   after the duplicate part (a nested header block that should have opened
   its own message but didn't — see cause 3), comparing the two copies as
   one blob diluted the match ratio enough that even a fuzzy whole-blob
   check said "not a duplicate" and printed the duplicate part anyway.
   **Fixed**: `_dedupe_prefix()` in `core.py` walks `addition`'s own lines
   from the top, trims any leading run that's already present (allowing OCR
   noise) in what's held, and keeps only the genuinely new remainder.
2. **Page-owner/Bates-stamp codes and committee banners leaking into body
   text.** `GARRY%07d` was never filtered (`REV%07d` already was); the
   multi-line "CONFIDENTIAL TREATMENT / REQUESTED - NOT FOR / CIRCULATION /
   COMMITTEE / MEMBERS AND STAFF ONLY LIP-NNNNNN" banner wasn't either.
   **Fixed**: both added to `FURNITURE` in `parse_po_emails.py` — safe
   regardless of `page_owner_map()`, which reads the raw, unfiltered text
   independently for exactly this reason.
3. **An inline-quote marker ending in `;` instead of `:`** ("On 17 Feb 2020,
   at 7:57 am, Garry, Robert F FP wrote;" — the scan misread the colon) —
   failed to match, so that reply never got its own entry and was glued into
   the PREVIOUS message's signature block instead (once `split_signature()`
   cuts to signature mode, everything to the end of the body is signature,
   with no further break point). **Fixed**: `[:;]` instead of `:` at the end
   of `DEFAULT_INLINE_QUOTE_RE`.

**Not fixed — a different, harder problem, left as a known limitation**: a
handful of entries (6 remaining in po-emails as of this writing, found by
scanning for any line over 30 characters repeated within one entry's own
content) still show a paragraph duplicated with NO furniture/stamp line and
no merge boundary involved at all — the duplication is already present
within what `segment()` collected as a SINGLE message's own body, most
likely a genuine page-transition rendering artifact in the source scan
itself (the tail of one page's text reappearing at the top of the next).
Fixing this needs detecting a repeated run of lines WITHIN one message's own
body (not across two different messages/entries, which is what
`_dedupe_prefix()` above handles) — a related but distinct algorithm, not
yet built. Worth revisiting once the §3 dedup work is in place, since that
will need very similar same-content-detection machinery anyway.

## 3. Deduplication to unique entries, with up/downstream links

**Status: built and verified** (`foia_parser/core.py`'s `dedupe_similar_entries()`,
run after `reconcile_zones()` and before thread-key assignment). 9 entries
collapsed across both corpora as of this writing (3 in po-emails, 6 in
farrar-fauci), zero chronology violations, deterministic across repeated
runs, every merge manually inspected for correctness (see the three
false-positive mechanisms below — each was caught this way, not by trusting
the numbers).

**The problem.** Every reply in a long thread reprints the *entire* prior
chain, so the same real email can appear verbatim (OCR noise aside) dozens
of times across the corpus — once as a top-level message in its own right,
and again inside every subsequent reply that quotes it. Today's parser
creates a **new entry** each time segmentation finds a boundary, so the same
real email currently exists as N near-duplicate entries, each a partial or
differently-OCR'd copy, scattered across the timeline.

**The goal**, per the ask: collapse each real email down to **one** entry —
the best-available representative — and represent the N-deep nesting it
came from as `reply_to`/`replied_by` edges between *unique* emails, not as
separate timeline entries.

**Matching "the same real email" across reprints, as built**: sender +
zone-corrected **date** (NOT also time — see below), with a body-similarity
check (not subject — too often "[NA]" to discriminate, and genuinely not
needed once body similarity is checked directly).

**The exact-time key was tried first and discarded** — confirmed empirically
unworkable: the same original message's own embedded quoted timestamp ("On
<date> at <time> ... wrote:") legitimately reads DIFFERENTLY each time it's
quoted, because each quoter's own mail client rendered that quoted stamp in
THEIR OWN zone before ever typing their reply (this IS §2's "frozen in the
replier's zone" principle, showing up a second time, now as a dedup problem
rather than a zone one). A real example: one short Jeremy Farrar message
recurs across farrar-fauci.json at **eleven different literal times** across
one calendar day, each pair scoring 0.6–1.00 body similarity — bucketing on
exact time caught none of them. Bucketing on sender + date alone, cross-time
matches held to a stricter similarity bar than same-time ones (weaker
corroborating evidence without a matching time), is what actually works.

**Three false-positive mechanisms found and fixed** while verifying matches
by hand (every one of these was a real entry this corpus produced, not a
hypothetical):

1. **Transitive clustering through a shared, unrelated intermediate.**
   Naive union-find (A matches B, B matches C ⇒ group A/B/C) wrongly merged
   three distinct one-line Robert Garry replies, each scoring high against a
   shared quoted tail, despite scoring **0.35** against each other directly.
   Fixed: clustering now compares every candidate only against a cluster's
   fixed, first-seen ANCHOR — never transitively, never against a growing
   aggregate.
2. **Comparing against the whole body+signature blob.** A correspondent's
   own identical multi-line signature (Edward Holmes's 5-line academic one)
   is often LONGER than a short message's real text, so four genuinely
   different one-line Holmes replies, each followed by his own identical
   sign-off, scored as near-duplicates purely on the shared signature.
   Fixed: comparison uses only the body segment, with the signature and any
   unrecovered nested quote boundary (a `From:`/`Date:` block, or an `On
   ... wrote:` marker, that segmentation failed to open as its own message
   — see §2b) truncated off first.
3. **`SequenceMatcher`'s match-sum conflating scattered coincidence with
   real duplication.** "Sounds correct to me." (21 characters) scored
   **0.95** against a long, entirely unrelated message — not from any real
   overlap, but from many tiny scattered character runs (the longest just 6
   characters) that happened to sum to 95% of the short string's length.
   Fixed: the single longest contiguous matching run must itself cover at
   least half the shorter text, not just the sum of every run found — a
   genuine duplicate (even noisy OCR) reads as mostly one long run broken by
   a handful of garbled characters, never many short coincidences.

**Picking the representative**, once a duplicate group is identified: most
header fields recovered (From + To + Cc + Subject + Sent, vs. a bare
inline-recovered From+Sent), then longest content, then earliest-appearing
copy as a final, stable tiebreak. Every non-representative copy's pages are
unioned into the representative's page range, and an explicit reply link
pointing at a dropped copy is redirected to the survivor — the same pattern
`merge_page_splits()` already used for its own, narrower exact-identity
merges.

**Known remaining limitation**: the content-union step (reusing
`_dedupe_prefix()`, §2b's fix for a related merge problem) walks the extra
copy's lines looking for each one already present somewhere in what's held,
and can be defeated by a long paragraph that two OCR passes line-wrapped
differently — neither copy's individual (differently-split) lines then
matches the other's closely enough, so the walk stops early and a
substantially-duplicate tail gets appended anyway. Confirmed in two of the
nine merges (a long teleconference invite, a long PIMS update) — the
duplicate IDENTIFICATION is correct in both (these genuinely are the same
real email), only the final rendered text is redundant rather than clean.
Fixing this properly means comparing the merge candidates as continuous
text (character-level, the way `_body_similarity()` already does) rather
than line-by-line, then mapping the cut point back to the original
(non-normalized) string — a real improvement, not attempted yet given the
false-positive risks above took priority to find and fix first.

**Depended on §2, as expected.** Confirmed directly: running this before the
zone fix would have bucketed on wrong timestamps throughout.

## 4. Thread panel: a third display alongside the PDF

**Status: built.** A 4th tab (`Timeline / Complementary / Tragicomedy /
Thread`) in the existing reader-pane tab mechanism — the user's own choice
over a genuinely separate always-visible panel, which would have needed new
layout space carved out of the results list, bookmarks rail, or PDF view.

**What it does**: a 🧵 `Thread` button appears on any card with `reply_to`
or a non-empty `replied_by` (email or Slack, kind-agnostic — reuses the
app's existing generic chip mechanism, not anything FOIA-email-specific).
Clicking it switches to the Thread tab and renders, Gmail-style: the full
upstream chain (walking `reply_to` back to the root, oldest first) with the
clicked message highlighted, then one level of `replied_by` dashed below as
"Answered by." Every non-current message is clickable to re-center the
panel on it — which also moves the underlying Timeline/PDF state (source +
page) to that message, so switching back to the Timeline tab afterward
shows the right page, without the Thread tab ever having touched the PDF
canvas itself. Verified end to end in a live headless-browser run (open →
click a downstream reply → re-centers → switch to Timeline → correct page).

**Downstream scope, as resolved**: one level of `replied_by` only — not the
full tree. A message with multiple reply branches (different people
answering the same email, possibly months apart) shows all of its direct
replies, but doesn't recurse into THEIR replies-of-replies; clicking one of
them re-centers the whole panel on it, which then shows that branch's own
upstream chain (now including the message you came from) and ITS direct
replies. This is the proposed default from the plan, applied, rather than a
dead end: walking deeper into a branch is still just another click away,
one level at a time, so nothing is permanently hidden — it just avoids
rendering a potentially enormous tree in one shot.

## 5. Build order

1. **Time-zone reconciliation (§2) — built**, including REV (confirmed with
   the user: US Pacific) and a third mailbox code, LIP (Lipkin, Columbia →
   `America/New_York`), found along the way.
2. **Dedup + representative-picking (§3) — built**, including three
   false-positive mechanisms found and fixed by manually verifying every
   merge (see §3) — not trusted on the entry-count delta alone.
3. **Thread panel UI (§4) — built**, a 4th tab alongside Timeline /
   Complementary / Tragicomedy, on top of the now-correct, deduplicated
   up/downstream links.

All four parts of this doc's original scope (§2 zones, §2b duplicate body
fixes, §3 dedup, §4 thread panel) are now built and verified. Each phase got
the same verification treatment: before/after entry-count and chronology
diffs, the full test suite, a live visual check of at least one concrete,
previously-wrong example, and a determinism check (the same release parsed
twice in separate fresh processes must byte-for-byte match — this caught one
real nondeterminism bug in §2's own page-owner tie-break). Final state:
73/66/33 tests pass (2 pre-existing, unrelated portrait-layout failures),
zero chronology violations in either corpus, deterministic across repeated
runs. Entry counts: po-emails 227 → 223 (4 merged: 1 bogus-timestamp fix
from an earlier phase, 3 genuine dedups); farrar-fauci 166 → 159 (1
bogus-timestamp fix, 6 genuine dedups).

**Remaining known limitations**, both already documented above rather than
silently left: the §2b line-wrap-defeated content-union in two dedup merges
(cosmetic duplication, not a wrong merge), and §2's own gap (zone
propagation only through the explicit inline-quote link, not the literal
nested-header case).

## 6. Follow-up fixes from live use

Found via actual use of the shipped Thread panel and Timeline, not held back
for a separate pass:

- **Literal nested headers now link too, narrowly.** `segment()`'s explicit
  `quotes_msg` link (§2/§3's foundation) extended from inline "`On ... wrote:`"
  markers to ALSO cover a literal nested `From:`/`Date:` header block --
  but only when it's found inside a message that is itself
  `recovered_inline`. A real case needed this: a 6-deep Andersen/Farzan
  "Re: Furin..." chain where the Thread panel only showed 3 links, missing
  the root message (introduced via a literal header, not a marker). Scoped
  deliberately narrow -- extending it to literal headers inside ORDINARY
  top-level messages too would reopen the Pope/NASEM false-link risk (§2b),
  which has no comparable guarantee of being genuine nested content.
- **The explicit-link chronology guard had a gap**: it only checked
  dated-vs-dated pairs, silently passing an UNDATED side through
  unverified. Found immediately after the fix above, via the test suite
  (`node test_app.mjs`) rather than a screenshot: a SECOND Pope/NASEM
  false-link case, this time with a garbled, unparseable stamp on the Pope
  side, sailed past the existing guard precisely because that guard had
  nothing to compare. Fixed to require BOTH sides dated before asserting
  the link at all -- fail closed, not open.
- **The timeline legend's per-source toggle was cosmetic-only.** Clicking a
  swatch hid that source's bars on the canvas (via Chart.js's own
  `setDatasetVisibility`) but never touched `kindFilter`-driven search,
  browse-window or timeline-click logic, which kept reading the full,
  unfiltered entry list regardless -- so a visually "hidden" source (e.g.
  Slack) still surfaced on a timeline click, confusing against the Types
  dropdown actually working. Fixed with a new `hiddenSegments` set, keyed
  on the same `source|kind` the legend already uses, consulted everywhere
  `kindFilter` already was (via a new shared `entryVisible()`) -- except the
  chart's OWN dataset list, which must stay complete so a hidden swatch can
  still be clicked back on.
- **Thread cards now show the full header** (From/To/Cc/Bcc/Subject, plus
  the local-time→ET stamp line and the zone evidence) instead of a
  condensed sender/date/subject one-liner -- reusing the exact same
  `content` header block and `stamp_line`/`zone_assumed` fields the main
  result card already shows, so there's no new data path to get wrong.
- **Downstream rendering** now follows an unbranching reply chain
  automatically (indented, joined by a left lineage line) and stops only at
  a genuine bifurcation (more than one direct reply), where each branch
  collapses behind its own "⬇ Downstream" button -- expanding one branch
  re-applies the same rule from there, so a heavily-forked thread never
  renders as one enormous tree, but any single branch can still be walked
  arbitrarily deep.
- **Dedup's matching key was still too strict about time.** §3's dedup
  originally bucketed on sender + calendar DATE (time itself deliberately
  excluded, per the "frozen in the replier's zone" finding below it) --
  but that still meant two appearances of the same real email were never
  even COMPARED if a few minutes of ordinary clock/provider drift pushed
  one of them across a midnight boundary into a different calendar-date
  string (23:58 one day vs 00:02 the next: 4 minutes apart in reality, two
  different buckets under date-string keying). Separately, "same time" was
  checked by exact HHMM string equality, so even same-day copies a few
  minutes apart (ordinary send/relay/rounding drift, not a zone issue at
  all) were scored under the STRICTER cross-time threshold rather than the
  looser one that drift like that should actually earn. Fixed: bucket by
  sender only, compare candidates by actual ELAPSED TIME (`_entry_minutes()`,
  an absolute minutes value from date+time together) rather than calendar-
  date or exact-time string equality -- within `close_minutes` (10) earns
  the lower bar; beyond that, up to `max_compare_days` (14, bounding the
  search so two sends months apart are never compared at all) needs the
  stricter one. Re-verified every resulting merge by hand again after this
  change, same as every prior iteration of §3's matching logic -- no new
  false merges found, only the same already-documented cosmetic line-wrap
  content-union artifact recurring in a couple of newly-caught genuine
  duplicates.
- **Downstream indentation was firing on every message, not just at a real
  fork.** A plain, unbranching reply chain (the common case) was being
  indented one step deeper per message -- a staircase -- when it should
  stay flat, stacked with the same "↓" connector the upstream chain already
  uses, exactly as far down as it goes. Indentation and the left lineage
  line are for signalling a genuine FORK only: two or more people replying
  or forwarding directly to the SAME email (one could answer within the
  hour, another forward it on years later -- both still shown, ordered by
  when, but neither "comes after" the other the way an ordinary chain
  does, which is specifically what the indent means). Fixed by tracking a
  separate `forkDepth` that only increments when actually crossing a fork
  boundary, not per downstream message -- a fork nested inside an
  already-expanded branch now indents one further step than ITS parent
  fork, not one step per message along the way to it. Branches at a fork
  are also now sorted chronologically before rendering. Upstream was
  already correct and needs no equivalent change: `reply_to` is
  single-valued by the data model, so it can never fork -- the one thing
  that could (forwarding two or more original emails on as attachments in
  one message) is an attachment relationship, not a reply one, and belongs
  on the main result card's own reply/forward chips, not the Thread panel.

All verified the same way as every other change in this doc: full test
suite (73/66/33, same 2 pre-existing portrait-layout failures), zero
chronology violations, deterministic across repeated runs, and a live
headless-browser reproduction of each specific reported symptom before and
after the fix.
