# Example content spec for data/build_extended_doc.py. Quillbase is an invented note-taking app; nothing here
# describes a real company. Angle-bracket slots (<...>) are left for you to fill on a real run.
# Build:  python3 build_extended_doc.py extended_spec_example.py
#
# Top-level fields: out, company, product, img_dir, accent, header, title, meta, lead, stage_why {stage: line},
# client_set [[page, group, address]] (the client's own benchmark pages; keep them private), sections.
# A section is {heading, new_page, blocks}. Block types: body, heading, subband, table, labels, figure, page_break,
# order_table, stage_table, library_table, pages_table. Tokens such as {N}, {of:2}, {n:43}, {blk:hero},
# {status:New}, {blocks} and {launch} are filled from the data (see build_extended_doc.py).

SPEC = {
    'out': 'Quillbase_comparison_template.docx',
    'company': 'Quillbase',
    'product': 'Quillbase',
    'img_dir': 'img',
    'accent': '404040',
    'header': 'Quillbase  ·  comparison template',
    'title': 'Quillbase comparison page template',
    'meta': 'Template recommendation, Month Year',
    'lead': ('One layout for every page that sets Quillbase against a single rival. The block list below comes '
             'from {N} vendor comparison pages coded against 50 section types; it has {blocks} blocks, '
             '{launch} of them needed at launch.'),
    'stage_why': {
        'Capture': 'Prove the reader landed on the right pair within one screen.',
        'Orient': 'Let a skimmer leave with an answer.',
        'Evaluate': 'Give the evidence row by row, rival strengths included.',
        'De-risk': 'Remove the reasons not to switch or not to trial.',
        'Convert': 'Offer one clear next step.',
    },
    'client_set': [],   # e.g. ['<Rival A> vs Quillbase', 'Vendor, notes', '<address>']
    'sections': [
        {'heading': 'Overview', 'blocks': [
            {'type': 'body', 'text': '<Two sentences: what Quillbase has today for comparisons, and what this template adds.>'},
            {'type': 'table', 'head': ['Choice', 'Reason from the benchmark'], 'widths': [45, 55], 'rows': [
                ['Lead with a short answer and a line on how the two differ.',
                 '{of:2} put a verdict in the first screen; {n:8} add a short summary.'],
                ['Give the rival at least one row or point.', 'Only {of:18} do, so it reads as fair.'],
                ['Say whether Quillbase can run alongside the rival.', '3 of the 9 SaaS pages answer this.'],
                ['Name a writer and a checker, and date the sources.', '{of:3} names an author; none names a checker.'],
            ]},
            {'type': 'figure', 'img': 'wire_vs_1.png', 'caption': 'Wireframe, part 1', 'source': 'Template draft'},
            {'type': 'figure', 'img': 'wire_vs_2.png', 'caption': 'Wireframe, part 2', 'source': 'Template draft'},
            {'type': 'figure', 'img': 'wire_vs_3.png', 'caption': 'Wireframe, part 3', 'source': 'Template draft'},
        ]},
        {'heading': 'Block order', 'new_page': True, 'blocks': [
            {'type': 'body', 'text': 'Statuses: {status:New} new, {status:Rework} rework, {status:Optional} optional, {status:Later} later.'},
            {'type': 'order_table'},
            {'type': 'stage_table'},
            {'type': 'figure', 'img': 'wire_vs_mobile.png', 'caption': 'Phone order', 'source': 'Template draft', 'max_h': 5.0},
        ]},
        {'heading': 'Block notes', 'new_page': True, 'blocks': [
            {'type': 'body', 'text': 'One note per block. What each note must settle is listed in reference/doc-structure.md.'},
            {'type': 'subband', 'text': 'First screen', 'status': 'New'},
            {'type': 'labels', 'pairs': [
                ('{blk:hero}', '<breadcrumb, H1 pattern, difference line rule>'),
                ('{blk:button}', '<label and target, shared with the hub>'),
                ('{blk:proof}', '<which proof points, and where each one is sourced>'),
            ]},
            {'type': 'subband', 'text': 'Comparison table', 'status': 'New'},
            {'type': 'labels', 'pairs': [
                ('{blk:table}', '<fixed row labels, one sentence per cell, who-leads tag>'),
                ('Row mapping', '<each item in the current pricing-page feature list: kept, merged, renamed or dropped>'),
            ]},
            {'type': 'body', 'text': '<Continue for the other blocks you build.>'},
        ]},
        {'heading': 'Rival categories', 'blocks': [
            {'type': 'table', 'head': ['Category', 'Rivals', 'Row the rival leads', 'Question the summary answers'],
             'widths': [22, 22, 26, 30],
             'rows': [['<category>', '<rivals>', '<row>', '<question>']]},
        ]},
        {'heading': 'Appendix: benchmark pages', 'new_page': True, 'blocks': [{'type': 'pages_table'}]},
        {'heading': 'Appendix: section library', 'new_page': True, 'blocks': [{'type': 'library_table'}]},
    ],
}
