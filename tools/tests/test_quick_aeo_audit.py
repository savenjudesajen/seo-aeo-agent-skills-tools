"""Tests for skills/quick-aeo-audit/data: the deck gate (deck_qc.py) and the deck helpers (deck_helpers.py).

    python3 -m unittest discover -s tools/tests -v

Needs python-pptx and Pillow (the helpers' own requirements); CI installs them. Decks are built in a
temporary folder and never written into the repo.
"""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "skills" / "quick-aeo-audit" / "data"
sys.path.insert(0, str(DATA))

import deck_helpers as H  # noqa: E402
import deck_qc  # noqa: E402
from pptx import Presentation  # noqa: E402
from pptx.enum.text import PP_ALIGN  # noqa: E402

# A footer well over the 40 characters that used to count it as a repeated block on every slide.
LONG_FOOTER = "Confidential | Prepared for Northwind Outdoor Co. | AI visibility audit, March 2027"
# Distinct body text per slide, so only the footer could repeat.
BODIES = [
    "Northwind is named on every branded question the engines were asked during this run.",
    "Category questions about trail running gear never bring the brand up on their own.",
    "Perplexity reads retailer roundups first and quotes their rankings almost word for word.",
    "Three comparison pages and two answer pages would cover most of the open questions.",
]


def new_deck():
    prs = Presentation()
    prs.slide_width, prs.slide_height = H.E(13.333), H.E(7.5)
    return prs


def build(slides, footer=LONG_FOOTER, logo_path=None):
    """slides: list of (title, body). Returns the saved deck's path."""
    prs = new_deck()
    for n, (title, body) in enumerate(slides):
        s = H.add_blank_slide(prs)
        H.add_chrome(prs, s, title, logo_path=logo_path, footer_text=footer, kicker="Section %d" % n)
        H._textbox(s, H.E(H.MARGIN), H.E(H.CONTENT_TOP), H.E(10), H.E(1), body, size=14)
        H.set_notes(s, "Say the finding.", "One line for the call.")
    H.renumber_footers(prs)
    path = Path(tempfile.mkdtemp()) / "deck.pptx"
    prs.save(path)
    return path


def gate(path, *args):
    """(exit code, printed report) of deck_qc on the deck."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = deck_qc.main([str(path)] + list(args))
    return code, out.getvalue()


class DeckGateChrome(unittest.TestCase):
    def test_long_footer_on_every_slide_is_not_a_repeated_block(self):
        path = build([("Finding %d" % n, b) for n, b in enumerate(BODIES)])
        code, report = gate(path)
        self.assertEqual(code, 0, report)

    def test_repeated_body_text_is_still_caught(self):
        same = "This exact sentence about trail running appears on two different slides of the deck."
        path = build([("One", same), ("Two", same), ("Three", BODIES[2])])
        code, report = gate(path)
        self.assertEqual(code, 1)
        self.assertIn("REPEATED STRING", report)
        self.assertNotIn("confidential", report.lower())  # the footer is not what it reports

    def test_footer_is_still_checked_for_tool_names_and_dashes(self):
        path = build([("One", BODIES[0]), ("Two", BODIES[1])], footer="Data: Semrush " + chr(0x2014) + " March 2027")
        code, report = gate(path)
        self.assertEqual(code, 1)
        self.assertIn("'Semrush'", report)
        self.assertIn("em dash", report)

    def test_wrong_page_number_in_the_footer_band_is_still_caught(self):
        path = build([("One", BODIES[0]), ("Two", BODIES[1])])
        prs = Presentation(str(path))
        for sh in prs.slides[1].shapes:
            if sh.has_text_frame and sh.text_frame.text.strip() == "2":
                H.set_simple(sh, "7")
        prs.save(str(path))
        code, report = gate(path)
        self.assertEqual(code, 1)
        self.assertIn("s2 shows '7'", report)


    def test_caption_just_above_the_footer_rule_is_content(self):
        caption = "Share of all brand mentions across fifty category questions, single-run baseline."
        prs = new_deck()
        for title, body in (("One", BODIES[0]), ("Two", BODIES[1])):
            s = H.add_blank_slide(prs)
            H.add_chrome(prs, s, title, footer_text="Confidential")
            H._textbox(s, H.E(H.MARGIN), H.E(H.CONTENT_TOP), H.E(10), H.E(1), body)
            H._textbox(s, H.E(H.MARGIN), H.E(6.8), H.E(10), H.E(0.18), caption, size=9)  # above the rule at 7.0 in
            H.set_notes(s, "Say it.", "Insight.")
        H.renumber_footers(prs)
        path = Path(tempfile.mkdtemp()) / "deck.pptx"
        prs.save(path)
        code, report = gate(path)
        self.assertEqual(code, 1)
        self.assertIn("share of all brand mentions", report)

    def test_grouped_shape_is_judged_as_content(self):
        # A group at y=1.5 in whose child coordinates start at 7.0 in: the child's own offset reads as the
        # footer band, but on the slide it is body text. Its repeat must still be caught.
        from lxml import etree
        same = "This sentence sits inside a group and repeats on two slides of the same deck."
        prs = new_deck()
        for title in ("One", "Two"):
            s = H.add_blank_slide(prs)
            H.add_chrome(prs, s, title, footer_text="Confidential")
            tb = H._textbox(s, H.E(H.MARGIN), H.E(7.0), H.E(10), H.E(0.4), same)
            grp = s.shapes.add_group_shape()
            grp._element.append(tb._element)  # moves the text box into the group
            xfrm = grp._element.grpSpPr.get_or_add_xfrm()
            for child in list(xfrm):
                xfrm.remove(child)
            a = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
            etree.SubElement(xfrm, a + "off", x=str(H.E(0.6)), y=str(H.E(1.5)))
            etree.SubElement(xfrm, a + "ext", cx=str(H.E(10)), cy=str(H.E(0.4)))
            etree.SubElement(xfrm, a + "chOff", x=str(H.E(0.6)), y=str(H.E(7.0)))
            etree.SubElement(xfrm, a + "chExt", cx=str(H.E(10)), cy=str(H.E(0.4)))
            H.set_notes(s, "Say it.", "Insight.")
        H.renumber_footers(prs)
        path = Path(tempfile.mkdtemp()) / "deck.pptx"
        prs.save(path)
        code, report = gate(path)
        self.assertEqual(code, 1)
        self.assertIn("inside a group", report)


class DeckGateCharts(unittest.TestCase):
    def test_chart_categories_are_checked(self):
        prs = new_deck()
        s = H.add_blank_slide(prs)
        H.add_chrome(prs, s, "Share of voice", footer_text="Confidential")
        H.add_bar_chart(s, H.E(0.6), H.E(1.4), H.E(12), H.E(4), ["Semrush", "Northwind " + chr(0x2014) + " outdoor"],
                        [30.0, 12.5], [H.GRAY, H.ACCENT])
        H.set_notes(s, "Say it.", "Insight.")
        H.renumber_footers(prs)
        path = Path(tempfile.mkdtemp()) / "deck.pptx"
        prs.save(path)
        code, report = gate(path)
        self.assertEqual(code, 1)
        self.assertIn("'Semrush'", report)
        self.assertIn("em dash", report)

    def test_brand_names_repeated_across_charts_are_not_a_repeated_block(self):
        brands = ["Northwind Outdoor Company", "Contoso Trail Supply Group", "Fabrikam Mountain Gear"]
        prs = new_deck()
        for n, body in enumerate(BODIES[:2]):
            s = H.add_blank_slide(prs)
            H.add_chrome(prs, s, "Finding %d" % n, footer_text="Confidential")
            H._textbox(s, H.E(H.MARGIN), H.E(H.CONTENT_TOP), H.E(10), H.E(1), body, size=14)
            H.add_bar_chart(s, H.E(0.6), H.E(2.6), H.E(12), H.E(3), brands, [1.0, 2.0, 3.0], [H.GRAY] * 3)
            H.set_notes(s, "Say it.", "Insight.")
        H.renumber_footers(prs)
        path = Path(tempfile.mkdtemp()) / "deck.pptx"
        prs.save(path)
        code, report = gate(path)
        self.assertEqual(code, 0, report)


class DeckGateTrackedBrands(unittest.TestCase):
    def test_tracked_tool_vendor_needs_allow_tool(self):
        path = build([("Profound leads category answers", BODIES[0]), ("Two", BODIES[1])], footer="Confidential")
        code, report = gate(path)
        self.assertEqual(code, 1)
        self.assertIn("'Profound'", report)
        code, report = gate(path, "--allow-tool", "Profound")
        self.assertEqual(code, 0, report)

    def test_full_brand_name_allows_the_listed_name(self):
        path = build([("Peec AI trails the suites", BODIES[0]), ("Two", BODIES[1])], footer="Confidential")
        self.assertEqual(gate(path)[0], 1)
        code, report = gate(path, "--allow-tool", "Peec AI")
        self.assertEqual(code, 0, report)

    def test_allowing_one_brand_keeps_the_others_forbidden(self):
        path = build([("Peec AI and Semrush lead", BODIES[0]), ("Two", BODIES[1])], footer="Confidential")
        code, report = gate(path, "--allow-tool", "Peec AI")
        self.assertEqual(code, 1)
        self.assertIn("'Semrush'", report)
        self.assertNotIn("'Peec'", report)


class ChromeTitleWidth(unittest.TestCase):
    def _title_width(self, prs, slide, title):
        return next(sh.width for sh in slide.shapes if sh.has_text_frame and sh.text_frame.text == title)

    def test_title_spans_the_content_width_without_a_logo(self):
        prs = new_deck()
        s = H.add_blank_slide(prs)
        H.add_chrome(prs, s, "A title")
        self.assertEqual(self._title_width(prs, s, "A title"), prs.slide_width - 2 * H.E(H.MARGIN))

    def test_title_stops_short_of_the_logo(self):
        from PIL import Image
        logo = Path(tempfile.mkdtemp()) / "logo.png"
        Image.new("RGB", (400, 100), "white").save(logo)  # 4:1 -> fits as 1.6 x 0.4 in
        prs = new_deck()
        s = H.add_blank_slide(prs)
        H.add_chrome(prs, s, "A title", logo_path=str(logo))
        expected = prs.slide_width - 2 * H.E(H.MARGIN) - H.E(1.6 + H.LOGO_GAP)
        self.assertEqual(self._title_width(prs, s, "A title"), expected)
        pic = [sh for sh in s.shapes if sh.shape_type == 13]  # MSO_SHAPE_TYPE.PICTURE
        self.assertEqual(len(pic), 1)
        self.assertEqual(pic[0].width, H.E(1.6))


class Takeaway(unittest.TestCase):
    def test_label_and_body_are_left_aligned(self):
        prs = new_deck()
        s = H.add_blank_slide(prs)
        H.add_takeaway(prs, s, "The body line.", label="Takeaway")
        box = s.shapes[-1]
        paras = box.text_frame.paragraphs
        self.assertEqual([p.text for p in paras], ["Takeaway", "The body line."])
        self.assertEqual([p.alignment for p in paras], [PP_ALIGN.LEFT, PP_ALIGN.LEFT])


class BarChart(unittest.TestCase):
    def test_native_chart_keeps_categories_as_text(self):
        prs = new_deck()
        s = H.add_blank_slide(prs)
        chart = H.add_bar_chart(s, H.E(0.6), H.E(1.4), H.E(12), H.E(4), ["Northwind", "Rival"], [12.5, 30.0],
                                [H.ACCENT, H.GRAY])
        self.assertEqual(list(chart.plots[0].categories), ["Northwind", "Rival"])
        self.assertTrue(chart.category_axis.reverse_order)

    def test_columns_keep_the_first_category_at_the_left(self):
        from pptx.enum.chart import XL_CHART_TYPE
        prs = new_deck()
        s = H.add_blank_slide(prs)
        chart = H.add_bar_chart(s, 0, 0, H.E(5), H.E(3), ["Home", "Sign in"], [40.0, 22.0], [H.GRAY, H.GRAY],
                                horizontal=False)
        self.assertEqual(chart.chart_type, XL_CHART_TYPE.COLUMN_CLUSTERED)
        self.assertFalse(chart.category_axis.reverse_order)

    def test_mismatched_lengths_are_refused(self):
        prs = new_deck()
        s = H.add_blank_slide(prs)
        with self.assertRaises(ValueError):
            H.add_bar_chart(s, 0, 0, H.E(5), H.E(3), ["A", "B"], [1.0], [H.ACCENT, H.GRAY])


if __name__ == "__main__":
    unittest.main()
