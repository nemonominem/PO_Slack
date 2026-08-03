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
