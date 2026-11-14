# Fictional worked example for data/lean_doc.py. ExampleCo (meal kits) has four live comparison pages, against
# CompetitorA, CompetitorB, CompetitorC and CompetitorD, on example.com. Nothing here describes a real company or
# engagement: the company findings are invented, the crop boxes are placeholders, and the pattern captions describe
# public pages you must re-capture and re-check.
# Build:  python3 lean_doc.py lean_spec_example.py --crop --render
# (--crop needs the raw captures in raw/ next to this file; without --crop the cropped figures must already be in img/.)
#
# Fields
#   out, raw_dir, img_dir     output file and the two image folders, relative to this file
#   month_year                printed in every Source line
#   author, accent            document author, accent colour as a hex string (the company's own, if it has one)
#   company_tag               tag text for the company's own captures (kind today)
#   never_mention             words the copy scan must not find (the user's never-mention list)
#   title, subtitle, basis    top of page 1
#   section1, section2        heading, intro or note, page_break (section 2 starts on a new page by default)
#   sources                   short key -> domain/path, used by a figure src (a literal domain/path also works)
#   crops                     figure name -> [raw capture name, [x0, y0, x1, y1]] in raw pixels
#   rows                      num, name, status (Keep, Rework, Add, Remove), do (the action, 30 words at most),
#                             optional page_break, and figrows: figure rows shown under the row band.
#                             A figure row has items, optional widths (inches, summing to 6.7) and chain
#                             (keep with the next figure row in the same band).
#   item                      img (a figure name, or a list of two to stack), w (inches), kind (today, or a pattern
#                             kind such as vendor or independent), name (the pattern site), src, cap (30 words at most)

SPEC = {
    'out': 'ExampleCo_head_to_head_pages.docx',
    'raw_dir': 'raw',
    'img_dir': 'img',
    'month_year': 'Month Year',
    'author': 'Your name',
    'accent': '404040',
    'company_tag': 'ExampleCo today',
    'never_mention': ['agency', 'client'],
    'title': 'ExampleCo head-to-head pages: what each section should do',
    'subtitle': 'One order for every page, the change each section needs, and an example of each',
    'basis': 'Based on the four live ExampleCo comparison pages and pages by other vendors, captured Month Year.',
    'section1': {
        'heading': '1. Page order',
        'intro': 'The same order on all four pages. Each status compares the plan with what the pages show today.',
    },
    'section2': {
        'heading': '2. Screenshots in page order',
        'page_break': True,
        'note': 'Each band repeats a row of the table above. Accent-colour tags mark ExampleCo\'s current pages; blue tags mark other sites, shown for their layout only and never for their claims.',
    },
    'sources': {
        'CA': 'example.com/compare/exampleco-vs-competitora',
        'CB': 'example.com/compare/exampleco-vs-competitorb',
        'CC': 'example.com/compare/exampleco-vs-competitorc',
        'CD': 'example.com/compare/exampleco-vs-competitord',
        'SE': 'semrush.com/vs/semrush-vs-ahrefs',
        'MO': 'monday.com/blog/project-management/asana-vs-monday-com-which-to-choose',
        'WF': 'webflow.com/vs/wordpress',
        'AH': 'ahrefs.com/vs/semrush',
        'ZD': 'zendesk.com/why-zendesk/zendesk-vs-freshdesk',
        'AT': 'airtable.com/airtable-vs-smartsheet',
        'IC': 'intercom.com/compare-intercom-vs-zendesk',
        'CU': 'clickup.com/compare/asana-vs-clickup',
    },
    # Placeholder boxes: measure the real ones on your own captures.
    'crops': {
        'r01_cb_hero': ['cb_hero', [0, 0, 1200, 500]],
        'r01_se_hero': ['se_hero', [0, 0, 1200, 500]],
        'r02_mo_summary': ['mo_summary', [0, 0, 1200, 400]],
        'r02_mo_fit': ['mo_fit', [0, 0, 1200, 400]],
        'r03_ca_grid': ['ca_grid', [0, 0, 1200, 600]],
        'r03_wf_cells': ['wf_cells', [0, 0, 1200, 600]],
        'r04_cd_cards': ['cd_cards', [0, 0, 1200, 400]],
        'r04_ah_rival_ahead': ['ah_rival_ahead', [0, 0, 1200, 400]],
        'r05_mo_verdicts': ['mo_verdicts', [0, 0, 1200, 600]],
        'r05_zd_pillars': ['zd_pillars', [0, 0, 1200, 600]],
        'r06_cc_price': ['cc_price', [0, 0, 1200, 400]],
        'r06_zd_basis': ['zd_basis', [0, 0, 1200, 500]],
        'r07_ic_without': ['ic_without', [0, 0, 1200, 400]],
        'r07_at_equivalents': ['at_equivalents', [0, 0, 1200, 500]],
        'r08_ca_quotes': ['ca_quotes', [0, 0, 1200, 400]],
        'r08_mo_ratings': ['mo_ratings', [0, 0, 1200, 400]],
        'r09_cb_faq': ['cb_faq', [0, 0, 1200, 500]],
        'r10_mo_more': ['mo_more', [0, 0, 1200, 300]],
        'r10_cu_footer': ['cu_footer', [0, 0, 1200, 300]],
        'r11_cc_band': ['cc_band', [0, 0, 1200, 400]],
        'r12_se_error_link': ['se_error_link', [0, 0, 1200, 300]],
        'r12_ah_dated_table': ['ah_dated_table', [0, 0, 1200, 500]],
        'r13_cb_video': ['cb_video', [0, 0, 1200, 500]],
    },
    'rows': [
        {
            'num': 1, 'name': 'Hero', 'status': 'Rework',
            'do': 'Put both names in every H1 and add one line under it on how the two differ.',
            'figrows': [
                {'widths': [3.35, 3.35], 'items': [
                    {'img': 'r01_cb_hero', 'w': 3.2, 'kind': 'today', 'src': 'CB',
                     'cap': 'CompetitorB page. The H1 names only the rival and there is no line on what sets ExampleCo apart.'},
                    {'img': 'r01_se_hero', 'w': 3.2, 'kind': 'vendor', 'name': 'Semrush', 'src': 'SE',
                     'cap': 'Two sentences under the H1 contrast what each product covers.'},
                ]},
            ],
        },
        {
            'num': 2, 'name': 'Short answer', 'status': 'Add',
            'do': 'Add a short answer under the hero, with one bullet where <Rival> is the better pick, then a choose-if list for each product.',
            'figrows': [
                {'widths': [3.35, 3.35], 'items': [
                    {'img': 'r02_mo_summary', 'w': 3.2, 'kind': 'vendor', 'name': 'monday.com', 'src': 'MO',
                     'cap': 'A summary near the top in which one point favours the rival.'},
                    {'img': 'r02_mo_fit', 'w': 3.0, 'kind': 'vendor', 'name': 'monday.com', 'src': 'MO',
                     'cap': 'A list for each product of who should pick it.'},
                ]},
            ],
        },
        {
            'num': 3, 'name': 'Side-by-side table', 'status': 'Rework', 'page_break': True,
            'do': 'Replace the tick marks with one sentence per cell, use the same rows on all four pages, and date the table.',
            'figrows': [
                {'widths': [3.35, 3.35], 'items': [
                    {'img': 'r03_ca_grid', 'w': 3.2, 'kind': 'today', 'src': 'CA',
                     'cap': 'CompetitorA page. Ticks and crosses only. Each of the four pages uses a different set of rows.'},
                    {'img': 'r03_wf_cells', 'w': 3.2, 'kind': 'vendor', 'name': 'Webflow', 'src': 'WF',
                     'cap': 'An icon plus a one-sentence reason in every cell.'},
                ]},
            ],
        },
        {
            'num': 4, 'name': 'Where ExampleCo leads', 'status': 'Keep',
            'do': 'Keep the sourced strength cards. Add one point where <Rival> leads, placed first.',
            'figrows': [
                {'widths': [3.35, 3.35], 'items': [
                    {'img': 'r04_cd_cards', 'w': 3.2, 'kind': 'today', 'src': 'CD',
                     'cap': 'CompetitorD page. Strength cards with a source link each. Nothing says where the rival does better.'},
                    {'img': 'r04_ah_rival_ahead', 'w': 3.2, 'kind': 'vendor', 'name': 'Ahrefs', 'src': 'AH',
                     'cap': 'Shows the one figure where the rival is ahead and explains it.'},
                ]},
            ],
        },
        {
            'num': 5, 'name': 'Sections by buying question', 'status': 'Add',
            'do': 'Add up to five sections named as buyer questions, each opening with its answer, including where <Rival> leads.',
            'figrows': [
                {'widths': [3.35, 3.35], 'items': [
                    {'img': 'r05_mo_verdicts', 'w': 3.0, 'kind': 'vendor', 'name': 'monday.com', 'src': 'MO',
                     'cap': 'Each heading is the dimension plus its verdict, a tie included.'},
                    {'img': 'r05_zd_pillars', 'w': 3.0, 'kind': 'vendor', 'name': 'Zendesk', 'src': 'ZD',
                     'cap': 'The sections and the table share the same few pillars.'},
                ]},
            ],
        },
        {
            'num': 6, 'name': 'Pricing and how it is bought', 'status': 'Rework',
            'do': 'Replace the undated rival price with how each one charges. Quote a price only where its owner publishes one, with the date checked.',
            'figrows': [
                {'widths': [3.35, 3.35], 'items': [
                    {'img': 'r06_cc_price', 'w': 3.2, 'kind': 'today', 'src': 'CC',
                     'cap': 'CompetitorC page. A rival price with no date or source.'},
                    {'img': 'r06_zd_basis', 'w': 3.2, 'kind': 'vendor', 'name': 'Zendesk', 'src': 'ZD',
                     'cap': 'Both price lists side by side, each with its billing basis.'},
                ]},
            ],
        },
        {
            'num': 7, 'name': 'Moving over or using both', 'status': 'Add',
            'do': 'Add a short block on moving from <Rival> and say plainly whether the two can be used together.',
            'figrows': [
                {'widths': [3.35, 3.35], 'items': [
                    {'img': 'r07_ic_without', 'w': 3.2, 'kind': 'vendor', 'name': 'Intercom', 'src': 'IC',
                     'cap': 'An FAQ answer on using the product without leaving the rival.'},
                    {'img': 'r07_at_equivalents', 'w': 3.0, 'kind': 'vendor', 'name': 'Airtable', 'src': 'AT',
                     'cap': 'The rival\'s modules mapped to its own, for a current rival user.'},
                ]},
            ],
        },
        {
            'num': 8, 'name': 'Proof', 'status': 'Rework',
            'do': 'Date each customer quote and add review-site ratings for both products, each with its review count.',
            'figrows': [
                {'widths': [3.35, 3.35], 'items': [
                    {'img': 'r08_ca_quotes', 'w': 3.2, 'kind': 'today', 'src': 'CA',
                     'cap': 'CompetitorA page. Customer quotes with no dates and no ratings.'},
                    {'img': 'r08_mo_ratings', 'w': 3.2, 'kind': 'vendor', 'name': 'monday.com', 'src': 'MO',
                     'cap': 'Review-site scores for both products, each with its review count.'},
                ]},
            ],
        },
        {
            'num': 9, 'name': 'FAQ', 'status': 'Keep',
            'do': 'Keep the questions. Put the answers in the page HTML so they are readable without a click.',
            'figrows': [
                {'items': [
                    {'img': 'r09_cb_faq', 'w': 5.2, 'kind': 'today', 'src': 'CB',
                     'cap': 'CompetitorB page. A short FAQ whose answers load only after a click.'},
                ]},
            ],
        },
        {
            'num': 10, 'name': 'Related comparisons', 'status': 'Add',
            'do': 'End each page with two related comparisons and a link to All comparisons.',
            'figrows': [
                {'widths': [3.35, 3.35], 'items': [
                    {'img': 'r10_mo_more', 'w': 3.2, 'kind': 'vendor', 'name': 'monday.com', 'src': 'MO',
                     'cap': 'An alternatives link and a run of further comparisons near the end.'},
                    {'img': 'r10_cu_footer', 'w': 3.2, 'kind': 'vendor', 'name': 'ClickUp', 'src': 'CU',
                     'cap': 'A footer block that links every comparison page.'},
                ]},
            ],
        },
        {
            'num': 11, 'name': 'Closing CTA', 'status': 'Keep',
            'do': 'Keep the closing band as it is on all four pages.',
            'figrows': [
                {'items': [
                    {'img': 'r11_cc_band', 'w': 5.2, 'kind': 'today', 'src': 'CC',
                     'cap': 'CompetitorC page. A full-width band that repeats the hero button.'},
                ]},
            ],
        },
        {
            'num': 12, 'name': 'How the page was checked', 'status': 'Add',
            'do': 'Number and date the sources, say who wrote and checked the page, and keep a dated change log.',
            'figrows': [
                {'widths': [3.35, 3.35], 'items': [
                    {'img': 'r12_se_error_link', 'w': 3.2, 'kind': 'vendor', 'name': 'Semrush', 'src': 'SE',
                     'cap': 'A data-as-of date under the table and a link to report an error.'},
                    {'img': 'r12_ah_dated_table', 'w': 3.2, 'kind': 'vendor', 'name': 'Ahrefs', 'src': 'AH',
                     'cap': 'An as-of month and a source link under a third-party table.'},
                ]},
            ],
        },
        {
            'num': 'Cut', 'name': 'Autoplay video (CompetitorB page)', 'status': 'Remove',
            'do': 'Remove the video that starts playing above the table; link it lower on the page if it stays.',
            'figrows': [
                {'items': [
                    {'img': 'r13_cb_video', 'w': 4.6, 'kind': 'today', 'src': 'CB',
                     'cap': 'CompetitorB page. A video plays on load above the table.'},
                ]},
            ],
        },
    ],
}
