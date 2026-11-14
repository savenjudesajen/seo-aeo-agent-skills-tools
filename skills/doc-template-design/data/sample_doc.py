# -*- coding: utf-8 -*-
"""Fixture: a short action document (reference/document-patterns.md) for an invented client, built through
doctemplate.py.

Used as the regression sample: build it once, approve the render, snapshot it with
`python3 audit.py snapshot sample.docx golden.json`, and later builds are checked against that snapshot
(`audit.py verify` and `audit.py xmlcheck`). The client, site and file are fictional.

Usage: python3 sample_doc.py out.docx [--theme slug] [--no-embed]
   or: python3 doctemplate.py --sample out.docx"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from doctemplate import Doc

CLIENT = 'Halden Bicycle Co.'
STAGING = 'staging.haldenbikes.example'
FILE = 'halden_redirects_v3.csv'


def build(out, theme=None, embed_fonts=True):
    d = Doc(short_title='Redirect map sign-off', client=CLIENT, theme=theme, embed_fonts=embed_fonts)
    d.title('Approve the redirect map before launch')
    d.meta(['Action request', CLIENT, d.t.meta_by() or 'Prepared by the SEO team', '3 March 2027'])
    d.lead('The new store launches with new page addresses, and the redirect map decides where every old address '
           'sends its visitors. A wrong row quietly loses the rankings that page has built up. We need your '
           'approval two working days before launch.')

    d.section('Context')
    d.body('The map in **%s** lists each old product and category address with its new home. We built it from '
           'the current catalogue; your team knows which retired models have a true successor and which do not.'
           % FILE)
    d.body('Everything can be checked on %s, which already runs the new site.' % STAGING, after=0)

    d.section('Tasks')
    d.table(['#', 'Task', 'Owner', 'Check'], [
        ('1', 'Sort the map by the Visits column so the busiest old pages come first.', 'Catalogue lead',
         'Top row has the most visits'),
        ('2', 'Open the new address of each of the top fifty rows on staging.', 'Catalogue lead',
         'Same product or topic on screen'),
        ('3', 'Mark rows that land on a weak match with "change" in the Decision column.', 'Catalogue lead',
         'No blank Decision on a weak match'),
        ('4', 'Confirm the rows the Note column flags as home-page redirects.', 'Web team',
         'Each one has a reason noted'),
    ], widths=[1, 9, 3, 4])

    d.section('Decision')
    d.facts([
        ('Recommendation', 'Send each retired model to the category page that replaced it, and name the old model '
                           'on that page.'),
        ('Alternative', 'Send retired models to the home page.'),
        ('Trade-off', 'Category redirects keep most of the old rankings; home-page redirects are treated much like '
                      'deleted pages.'),
        ('Decide by', 'The same day as the map approval.'),
    ], label_w=0.22)

    d.section('If something blocks you')
    d.bullets(['Staging asks for a login: the web team can issue one for the review.',
               'A whole category is going away: write "retired" in the Decision column and we will propose a home.',
               'Addresses carry tracking tags: ignore everything after the question mark; one rule handles them.'])

    d.section('After you finish')
    d.numbered(['Save the edited file back to the shared project folder.',
                'We load the approved map on staging and test every row.',
                'You get a list of any rows that failed, with fixes, before launch day.'])
    return d.save(out)


if __name__ == '__main__':
    a = sys.argv[1:]
    th = a[a.index('--theme') + 1] if '--theme' in a else None
    print(build(a[0] if a and not a[0].startswith('--') else 'sample.docx', theme=th,
                embed_fonts='--no-embed' not in a))
