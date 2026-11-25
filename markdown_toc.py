#!/usr/bin/env python3
"""Generate a Markdown table of contents from ATX headings."""
import argparse
import re
from pathlib import Path
from urllib.parse import quote

FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
HEADING = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+|$)(.*)$")
INLINE_LINK = re.compile(r"!?\[([^\]]+)\]\([^)]*\)")


def headings(lines):
    fence = None
    for line in lines:
        marker = FENCE.match(line)
        if fence is not None:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
            continue
        if marker and (marker[1][0] == "~" or "`" not in marker[2]):
            fence = marker[1]
            continue
        match = HEADING.match(line)
        if match:
            title = re.sub(r"[ \t]+#+[ \t]*$", "", match[2]).strip()
            title = INLINE_LINK.sub(r"\1", title)
            title = title.replace("`", "")
            if title:
                yield len(match[1]), title


def table(lines, minimum, maximum):
    used = set()
    entries = []
    for level, title in headings(lines):
        plain = re.sub(r"(?<!\w)[*_]+|[*_]+(?!\w)", "", title)
        base = re.sub(r"[^\w\- ]", "", plain.lower()).replace(" ", "-")
        slug, suffix = base, 0
        while slug in used:
            suffix += 1
            slug = f"{base}-{suffix}"
        used.add(slug)
        if minimum <= level <= maximum:
            entries.append((level, title, slug))
    depths = []
    for level, title, slug in entries:
        while depths and depths[-1] >= level:
            depths.pop()
        escaped = re.sub(r"([\\\[\]])", r"\\\1", title)
        yield f"{'  ' * len(depths)}- [{escaped}](#{quote(slug)})"
        depths.append(level)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--min", type=int, default=2)
    parser.add_argument("--max", type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.min <= args.max <= 6:
        parser.error("heading levels must satisfy 1 <= min <= max <= 6")
    try:
        print("\n".join(table(args.file.read_text(encoding="utf-8-sig").splitlines(), args.min, args.max)))
    except (OSError, UnicodeError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
