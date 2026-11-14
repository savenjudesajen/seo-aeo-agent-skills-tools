#!/usr/bin/env python3
"""Gate for the page-structure deliverable (.docx). Run it before you deliver; it must print PASS.

Checks, in document order:
  1. banned words: AI-tell vocabulary from the skill's writing rules;
  2. required parts: Part 1, Part 2, Part 2b, Part 3, Part 4 and the Appendix headings;
  3. captions: every embedded image is followed by a caption that names its source URL ("Source: <url>");
  4. leftovers: template placeholders ("TBD", "[image: ...]", "TODO", "YYYY-MM-DD", lorem ipsum) and the
     builder's sample URLs.

Standard library only, offline. Reads word/document.xml from the .docx zip.
usage: python3 check_deliverable.py <deliverable>.docx
exit:  0 = PASS, 1 = findings, 2 = the file could not be read
"""
import re
import sys
import zipfile
import xml.etree.ElementTree as ET


def local(tag):
    """Element name without its XML namespace (WordprocessingML: p, t, drawing, pict)."""
    return tag.rsplit("}", 1)[-1]


def descendants(el, name):
    return (e for e in el.iter() if local(e.tag) == name)


BANNED = [
    (r"(?i)\bleverag(?:e|es|ed|ing)\b", "leverage"),
    (r"(?i)\brobust(?:ly|ness)?\b", "robust"),
    (r"(?i)\bgenuine(?:ly)?\b", "genuine / genuinely"),
    (r"(?i)\bseamless(?:ly)?\b", "seamless"),
    (r"(?i)\bdelv(?:e|es|ed|ing)\b", "delve"),
    (r"(?i)\btestament\b", "testament"),
    (r"(?i)\bunderscor(?:e|es|ed|ing)\b", "underscore"),
    (r"(?:^|\s)Evidence:", '"Evidence:" as a label'),
    (r"(?i)\bconclusions[- ]first\b", "conclusions-first"),
]

REQUIRED_PARTS = [
    (r"^Part 1\b", "Part 1 (recommended section list)"),
    (r"^Part 2\b(?!b)", "Part 2 (sequenced blueprint)"),
    (r"^Part 2b\b", "Part 2b (principles cross-check)"),
    (r"^Part 3\b", "Part 3 (current page, section by section)"),
    (r"^Part 4\b", "Part 4 (missing sections with examples)"),
    (r"^Appendix\b", "Appendix (sources and method)"),
]

LEFTOVERS = [
    (r"\bTBD\b", "TBD placeholder"),
    (r"\[image:", "missing image placeholder"),
    (r"\bTODO\b", "TODO"),
    (r"YYYY-MM-DD", "date placeholder"),
    (r"(?i)lorem ipsum", "lorem ipsum"),
    (r"https?://www\.example\.com/product\b", "the builder's sample page URL"),
    (r"competitor-a\.example", "the builder's sample competitor URL"),
]

CAPTION_SOURCE = re.compile(r"Source:\s*(?:https?://)?[\w-]+(?:\.[\w-]+)+\S*", re.I)


def paragraphs(path):
    """Yield (text, has_image) for every paragraph in document order, tables included."""
    with zipfile.ZipFile(path) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
    for p in descendants(root, "p"):
        text = "".join(t.text or "" for t in descendants(p, "t")).strip()
        has_image = any(True for _ in descendants(p, "drawing")) or any(True for _ in descendants(p, "pict"))
        yield text, has_image


def check(path):
    paras = list(paragraphs(path))
    findings = []

    for i, (text, _) in enumerate(paras):
        for pat, label in BANNED:
            if re.search(pat, text):
                findings.append("banned word (%s) in paragraph %d: %s" % (label, i + 1, text[:80]))
        for pat, label in LEFTOVERS:
            if re.search(pat, text):
                findings.append("leftover (%s) in paragraph %d: %s" % (label, i + 1, text[:80]))

    texts = [t for t, _ in paras if t]
    for pat, label in REQUIRED_PARTS:
        if not any(re.search(pat, t) for t in texts):
            findings.append("missing part: %s" % label)

    for i, (_, has_image) in enumerate(paras):
        if not has_image:
            continue
        caption = next((t for t, img in paras[i + 1:] if t or img), "")
        if not CAPTION_SOURCE.search(caption):
            findings.append("image in paragraph %d has no caption with a source URL (next text: %r)"
                            % (i + 1, caption[:60]))

    return findings, sum(1 for _, img in paras if img)


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip())
        return 2
    try:
        findings, images = check(argv[1])
    except (OSError, KeyError, zipfile.BadZipFile, ET.ParseError) as exc:
        print("ERROR: cannot read %s as a .docx (%s)" % (argv[1], exc))
        return 2
    for f in findings:
        print("FAIL:", f)
    print("%d image(s) checked." % images)
    if findings:
        print("FAIL (%d finding(s))" % len(findings))
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
