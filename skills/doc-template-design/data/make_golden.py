# -*- coding: utf-8 -*-
"""Make a golden reference from a template export: remove the images you do not want in the comparison (usually
the logo) and keep every other part byte for byte. Used when you capture a client's own template
(reference/adopt-a-client-template.md): the rebuild is compared against this file's render.

    python3 make_golden.py original.docx golden.docx --image-name logo [--image-name wordmark]

Every drawing run whose XML mentions one of the names (its docPr name, description or media file) is removed
from the headers, footers and body, with its relationship and media part. Then render and fingerprint it:
    python3 audit.py snapshot golden.docx golden.json
Standard library only."""
import re
import sys
import zipfile


def main(argv):
    src, dst = argv[0], argv[1]
    names = [argv[i + 1] for i, a in enumerate(argv) if a == '--image-name']
    if not names:
        sys.exit('give at least one --image-name (part of the image name to remove)')
    pat = '|'.join(re.escape(n) for n in names)
    drawing = re.compile(r'<w:r(?: [^>]*)?>(?:(?!</w:r>).)*?<w:drawing>(?:(?!</w:r>).)*?(?:%s)(?:(?!</w:r>).)*?'
                         r'</w:drawing>(?:(?!</w:r>).)*?</w:r>' % pat, re.S | re.I)
    zin = zipfile.ZipFile(src)
    removed_media = set()
    texts = {}
    for it in zin.infolist():
        n = it.filename
        if re.match(r'word/(document|header\d*|footer\d*)\.xml$', n):
            s = zin.read(n).decode('utf-8')
            hits = drawing.findall(s)
            for h in hits:
                removed_media.update(re.findall(r'r:embed="([^"]+)"', h))
            texts[n] = drawing.sub('', s)
            if hits:
                print('%s: %d image run(s) removed' % (n, len(hits)))
    drop_parts = set()
    with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
        rels = {}
        for it in zin.infolist():
            n = it.filename
            if n.endswith('.rels') and n.startswith('word/_rels/'):
                owner = 'word/' + n[len('word/_rels/'):-len('.rels')]
                s = zin.read(n).decode('utf-8')
                if owner in texts:
                    still = texts[owner]
                    for rid, target in re.findall(r'<Relationship Id="([^"]+)" Type="[^"]+/image" Target="([^"]+)"/>', s):
                        if rid in removed_media and ('"%s"' % rid) not in still:
                            s = re.sub(r'<Relationship Id="%s" [^>]*/>' % re.escape(rid), '', s)
                            drop_parts.add('word/' + target)
                rels[n] = s
        for it in zin.infolist():
            n = it.filename
            if n in drop_parts:
                print('media part removed: ' + n)
                continue
            data = texts.get(n) or rels.get(n)
            zout.writestr(it, data.encode('utf-8') if data is not None else zin.read(n))
    print(dst)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1:])
