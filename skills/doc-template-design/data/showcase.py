# -*- coding: utf-8 -*-
"""Every block in one document: for eyeballing after a change to doctemplate.py, and the theme preview a user
confirms before a client theme is used (with --theme, a last section lists the theme's colours as swatches, its
fonts set in themselves, any substituted font and the evidence behind each value).

Usage: python3 showcase.py out.docx [image1.png image2.png] [--theme slug|themes/x.json] [--no-embed]
(images optional; neutral placeholders are drawn when absent)"""
import datetime
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from doctemplate import SZ, Doc, cell, para, row, run, table_xml


def _placeholder(path, w=1200, h=700, label='Screenshot'):
    from PIL import Image, ImageDraw
    im = Image.new('RGB', (w, h), (245, 246, 247))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, h - 1], outline=(205, 208, 212), width=3)
    d.line([0, 0, w, h], fill=(225, 228, 231), width=3)
    d.line([0, h, w, 0], fill=(225, 228, 231), width=3)
    d.text((30, 30), label, fill=(90, 99, 110))
    im.save(path)
    return path


def theme_section(d):
    """Colours as swatches with their paired text, fonts set in themselves, substitutes and evidence."""
    t = d.t
    d.section('Theme: %s' % t.client, new_page=True)
    ws = d._widths([3, 3, 5], 3)
    trs = [row([cell(w, para(run(h, **d._s(color=t.accent_text, sz=SZ['cell']))), fill=t.accent, valign='center')
                for h, w in zip(('Role', 'Colour', 'Sample'), ws)], header=True)]
    items = [('Table header row', t.accent, t.accent_text, 'Header row'), ('Stripe (sections, lead)', t.stripe, None, ''),
             ('Panel (fact labels, sections)', t.panel, t.ink, 'Fact label'),
             ('Section number on panel', t.panel, t.number, '3'), ('Ink', 'FFFFFF', t.ink, 'Body text'),
             ('Title', 'FFFFFF', t.title, 'Document title'), ('Muted', 'FFFFFF', t.muted, 'Meta line, notes, sources'),
             ('Rules', t.rule, None, '')]
    items += [('Chip: ' + k, f, c, k.upper()) for k, (f, c) in t.status.items()]
    for role, fill, col, sample in items:
        hexes = fill.upper() + (' / ' + col.upper() if col else '')
        samp = para(run(sample, **d._s(color=col, sz=SZ['cell']))) if col else para(run(' ', **d._b()))
        trs.append(row([cell(ws[0], para(run(role, **d._s(sz=SZ['cell'])))),
                        cell(ws[1], para(run(hexes, **d._b(sz=SZ['cell'])))),
                        cell(ws[2], samp, fill=fill, valign='center')]))
    d._add('table', table_xml(ws, trs, t.rule), ' '.join(i[0] for i in items))
    f, subs = t.fonts, t.spec.get('substitutes') or {}
    rows = [('Title font', f['title'], t.title_font, t.title_bold), ('Body font', f['body'], t.body_font, t.body_bold),
            ('Strong font (labels, headers%s)' % ('' if f.get('section') else ', sections'), f['strong'],
             t.strong_font, t.strong_bold)]
    if f.get('section'):
        rows.append(('Section font%s' % (', in capitals' if t.section_caps else ''), f['section'], t.section_font,
                     t.section_bold))
    ws2 = d._widths([3, 7], 2)
    trs = []
    for label, r, font, bold in rows:
        sample = '%s %d:  The quick brown fox jumps over the lazy dog 0123456789' % (r['family'], int(r.get('weight', 400)))
        trs.append(row([cell(ws2[0], para(run(label, **d._s(sz=SZ['cell']))), fill=t.panel),
                        cell(ws2[1], para(run(sample, font=font, bold=bold, color=t.ink, sz=SZ['cell'])))]))
    if subs:
        trs.append(row([cell(ws2[0], para(run('Licensed fonts replaced', **d._s(sz=SZ['cell']))), fill=t.panel),
                        cell(ws2[1], para(run('; '.join('%s is licensed, documents use %s' % kv for kv in subs.items()),
                                              **d._b(sz=SZ['cell']))))]))
    d._add('table', table_xml(ws2, trs, t.rule), ' '.join(r[0] for r in rows))
    why = (t.spec.get('provenance') or {}).get('why') or {}
    keys = [k for k in ('scheme', 'accent', 'highlight', 'ink', 'title', 'muted', 'panel', 'rule', 'status',
                        'body_font', 'title_font', 'section_font') if k in why]
    if keys:
        d.minor('Evidence behind each value')
        d.facts([(k.replace('_', ' ').capitalize(), '~' + why[k]) for k in keys], label_w=0.22)


def build(out, img1=None, img2=None, theme=None, embed_fonts=True):
    tmp = tempfile.mkdtemp(prefix='showcase-')        # placeholders stay out of the output folder
    img1 = img1 or _placeholder(os.path.join(tmp, 'ph1.png'), label='Figure image, 1200 x 700')
    img2 = img2 or _placeholder(os.path.join(tmp, 'ph2.png'), 900, 900, 'Square image')
    probe = Doc('x', theme=theme, embed_fonts=False)
    client = 'Sample client' if probe.t.default else probe.t.client
    d = Doc(short_title='Block showcase' if probe.t.default else 'Theme preview', client=client, theme=theme,
            embed_fonts=embed_fonts)
    d.title('Every block in the layout' if d.t.default else 'Every block in the %s theme' % client)
    d.meta(['Reference' if d.t.default else 'Theme preview', client, d.t.meta_by(),
            datetime.date.today().strftime('%d %B %Y').lstrip('0')])
    d.lead('The lead states the ask or the answer in two or three sentences, behind a stripe in the accent. '
           'Everything below keeps the layout\'s spacing and type scale%s.' % (
               '' if d.t.default else ' in %s\'s colours and fonts' % client))
    d.section('Fact table')
    d.facts([('Label', '**Bold value**\n~A muted note under the value.'),
             ('Second label', 'A plain value that wraps onto a second line when it runs long enough to need one.')])
    d.section('Table with a header row and a status column')
    d.table(['#', 'Section', 'Status', 'Why'], [
        ('1', 'Answer-first introduction', 'New', 'The answer before the story.'),
        ('2', 'Comparison table', 'Rework', 'Add the missing columns.'),
        ('3', 'Customer quotes', 'Keep', 'Already does the job.'),
        ('4', 'Second sign-up form', 'Remove', 'One ask per page.'),
        ('5', 'Video walkthrough', 'Optional', 'Only if one exists.'),
        ('6', 'Pricing detail', 'Later', 'Waits on the client.'),
    ], widths=[1, 6, 2, 7], status_col=2)
    d.body('A body paragraph after a table gets a little air above. **Bold segments** work in any text.')
    d.section('Subsections, minor headings and lists')
    d.body('A section followed by body text needs nothing between them.')
    d.subsection('Subsection with a status chip', 'New')
    d.minor('Minor heading')
    d.bullets(['First bullet.', 'Second bullet.', 'Third bullet, the last one gets the section spacing.'])
    d.subsection('Another status', 'Rework')
    d.facts([('What it is', 'Fact tables sit under subsections for short specs.'),
             ('Verdict', 'Lead with the change, then the reason.')], label_w=0.22)
    d.subsection('Without a chip')
    d.numbered(['A numbered step.', 'Another numbered step.'])
    d.note('A muted note for caveats and asides.')
    d.section('Figures')
    d.figure(img1, 'The finding the image proves, in one line', 'example.com/page, captured on the build date', max_h=3.0)
    d.figure_pair((img1, 'Left sub-caption'), (img2, 'Right sub-caption'), 'Two images side by side', 'example.com',
                  max_h=2.2)
    d.appendix('Lettered appendix', new_page=False)
    d.table(['Item', 'Count'], [('Rows in small type', '12'), ('Another row', '3')], widths=[4, 1], sz=17,
            bold_first=True, zebra=True)
    if not d.t.default:
        theme_section(d)
    return d.save(out)


if __name__ == '__main__':
    args = sys.argv[1:]
    theme = None
    if '--theme' in args:
        i = args.index('--theme')
        theme = args[i + 1]
        del args[i:i + 2]
    embed = '--no-embed' not in args
    args = [x for x in args if x != '--no-embed']
    print(build(args[0] if args else 'showcase.docx', *(args[1:3]), theme=theme, embed_fonts=embed))
