import unittest

from markdown_toc import table


class MarkdownTocTests(unittest.TestCase):
    def test_invalid_backtick_fence_preserves_headings(self):
        lines = ["```lang`bad", "## Visible"]
        self.assertEqual(list(table(lines, 2, 4)), ["- [Visible](#visible)"])

    def test_skips_valid_fences(self):
        lines = ["````python", "## Hidden", "```", "## Also hidden", "````", "## Visible"]
        self.assertEqual(list(table(lines, 2, 4)), ["- [Visible](#visible)"])

    def test_duplicate_outside_requested_heading_levels(self):
        lines = ["# Intro", "## Intro", "#### Child"]
        self.assertEqual(
            list(table(lines, 2, 4)),
            ["- [Intro](#intro-1)", "  - [Child](#child)"],
        )

    def test_inline_link_and_unicode_heading(self):
        self.assertEqual(
            list(table(["## [Café](https://example.com)"], 2, 4)),
            ["- [Café](#caf%C3%A9)"],
        )
