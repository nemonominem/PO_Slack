"""Shared Slack system-notice detection, used by both part1 and part2 builders
so system events (channel joins/renames/archives, ...) are attributed to the
same synthetic 'Slack Notice' sender in both parts rather than being
conflated with the mentioned person's authored chat messages."""

import re

NOTICE_PATTERNS = [
    re.compile(r"^joined\b", re.I),
    re.compile(r"^(un)?archived the (private )?channel", re.I),
    re.compile(r"^renamed the channel from", re.I),
    re.compile(r"^set the channel (topic|purpose)", re.I),
    re.compile(r"^added .* (to|as) this channel", re.I),
    re.compile(r"^removed .* from", re.I),
    re.compile(r"^left (the )?channel", re.I),
]


def apply_notice_normalization(sender, content):
    """Re-attribute Slack system-event messages to a synthetic 'Slack Notice'
    sender, folding the real actor's name back into the content text."""
    stripped = content.strip()
    # Drop a leading OCR-garbage icon glyph (e.g. "@ joined ...") before testing.
    probe = re.sub(r"^[^A-Za-z]+", "", stripped)
    for pat in NOTICE_PATTERNS:
        if pat.match(probe):
            return "Slack Notice", (sender + " " + probe).strip()
    return sender, content


# ── document kinds ──────────────────────────────────────────────────────────
# Every entry carries a `kind`, so the app can list, filter and count box
# types across every release it merges (Slack, FOI'd email, document, ...).
# The taxonomy and the recipe for adding a source are in SPEC.md.

KIND_SLACK = "slack"          # an authored chat message
KIND_ATTACHMENT = "attachment"  # a released document that exists as its own entry
KIND_NOTE = "note"            # publisher/system material, not a document


def entry_kind(sender, attachments=None):
    """Classify a Slack entry.

    A Slack message is a Slack message whether or not it carries a file: the
    files it carries are shown as chips on the card, not as a whole-message
    reclassifier. Bucketing file-carrying messages as `attachment` meant the
    "Slack" count silently dropped the ~1000 messages that happened to attach
    something -- which is what made the numbers look suspiciously round.

    Only Slack's own system events (channel created, joined, renamed, archived)
    are a different kind (`note`), the same reasoning that gives the Fauci
    diary's release note its own box. `attachment` stays reserved for a released
    document that is its own entry (like the Fauci diary's report) and is unused
    here.
    """
    if sender == "Slack Notice" or sender == "USLACKBOT":
        return KIND_NOTE
    return KIND_SLACK
