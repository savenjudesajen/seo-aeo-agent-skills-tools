"""Dump a .pptx template's structure before you edit it.

Usage: python3 dump_pptx.py Template.pptx

Prints slide size, each slide's layout, every shape's name / type / position / size, text by
paragraph level, tables (row x column count and cell contents) and speaker notes. You need this
before editing a template: it tells you which shape index holds what and how many rows each table
has (template tables silently drop extra rows).

Builder script: needs python-pptx.
"""
import sys

from pptx import Presentation
from pptx.util import Emu

EMU_PER_INCH = 914400


def dump(path):
    prs = Presentation(path)
    print(f"FILE: {path}")
    print(f"SLIDE SIZE: {prs.slide_width} x {prs.slide_height} EMU = "
          f"{prs.slide_width / EMU_PER_INCH:.2f} x {prs.slide_height / EMU_PER_INCH:.2f} in")
    print(f"NUM SLIDES: {len(prs.slides)}")
    print("=" * 100)
    for i, slide in enumerate(prs.slides, 1):
        try:
            layout = slide.slide_layout.name
        except Exception:
            layout = "?"
        print(f"\n--- SLIDE {i} | layout={layout} ---")
        for idx, sh in enumerate(slide.shapes):
            info = f"  #{idx} [{sh.name}] type={sh.shape_type}"
            try:
                info += (f" pos=({Emu(sh.left).inches:.2f},{Emu(sh.top).inches:.2f})"
                         f" size=({Emu(sh.width).inches:.2f}x{Emu(sh.height).inches:.2f})")
            except Exception:
                pass
            print(info)
            if sh.has_text_frame:
                for para in sh.text_frame.paragraphs:
                    txt = "".join(r.text for r in para.runs)
                    if txt.strip():
                        print(f"      | lvl{para.level}: {txt}")
            if getattr(sh, "has_table", False) and sh.has_table:
                tbl = sh.table
                print(f"      TABLE {len(tbl.rows)}x{len(tbl.columns)}")
                for r in tbl.rows:
                    print("       ROW:", " | ".join(c.text.replace("\n", " / ") for c in r.cells))
        if slide.has_notes_slide:
            notes = slide.notes_slide.notes_text_frame.text.strip()
            if notes:
                print(f"  NOTES: {notes[:600]}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python3 dump_pptx.py Template.pptx")
    dump(sys.argv[1])
