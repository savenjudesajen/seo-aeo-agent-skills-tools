#!/usr/bin/env python3
"""Pairwise page similarity from embedding vectors or page text (standard library only, offline).

Writes a url_a,url_b,similarity,method CSV that run_audit.py --pairs reads. Use it when the crawler's
"semantically similar" export only lists nearest neighbours above its threshold (0.95 by default), or when
some pages have no embedding vector.

Usage:
    python similarity_pairs.py --vectors internal.csv [--texts page_texts.csv] [--out similarity.csv] [--min 0.70]
    python similarity_pairs.py --texts page_texts.csv [--out similarity.csv] [--min 0.70]

Inputs
    --vectors  The crawler's Internal export: an Address (or URL) column and the embedding column
               ("Extract semantic embeddings from page", or name it with --vector-column). The vector may be
               written as "0.1,0.2,..." or "[0.1, 0.2, ...]".
    --texts    One row per page with columns URL and Text: the visible main content (navigation, footer and
               boilerplate removed), e.g. from your scrape. Give the text of EVERY page in scope, including
               pages that have a vector: a page without a vector can only be compared with pages whose text
               is in this file, and the TF-IDF weights are fitted over all of it.

Method
    embedding  cosine similarity of the two vectors.
    text       TF-IDF cosine fitted over every page in --texts (word unigrams and bigrams, English stop words
               removed). Each page without a vector is compared with every other page in the file. Terms
               found on more than --max-df of the pages are dropped only when the file has at least
               MIN_DOCS_FOR_MAX_DF (20) pages; a smaller file gets a warning that its scores are rough. Text
               scores run lower than embedding scores for the same pair: read them against their own bands
               and say so in Research_Notes.
A text pair is written only when at least one of the two pages has no vector.

Run time grows with the square of the page count (a few minutes per thousand pages with vectors).
"""

import argparse
import csv
import math
import re
import sys
from collections import Counter, defaultdict
from urllib.parse import unquote

STOP = set("""a about above after again against all am an and any are as at be because been before being below
between both but by can could did do does doing down during each few for from further had has have having he
her here hers herself him himself his how i if in into is it its itself just me more most my myself no nor not
now of off on once only or other our ours ourselves out over own same she should so some such than that the
their theirs them themselves then there these they this those through to too under until up very was we were
what when where which while who whom why will with would you your yours yourself yourselves""".split())
DEFAULT_VECTOR_COLUMN = "Extract semantic embeddings from page"
MIN_DOCS_FOR_MAX_DF = 20  # below this many pages of text, a max-df cut would drop the shared topic words


def norm(url):
    u = unquote((url or "").strip())
    if u.endswith("/") and u.count("/") > 3:
        u = u[:-1]
    return u


def pick(row, *names):
    lower = {k.strip().lower(): v for k, v in row.items() if k}
    for n in names:
        if n.lower() in lower:
            return lower[n.lower()]
    return None


def load_vectors(path, column):
    vecs, crawled = {}, set()
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            url = pick(row, "Address", "URL")
            if not url:
                continue
            crawled.add(norm(url))
            raw = pick(row, column) or ""
            parts = [p for p in re.split(r"[\s,\[\]]+", raw) if p]
            try:
                v = [float(p) for p in parts]
            except ValueError:
                continue
            n = math.sqrt(sum(x * x for x in v))
            if v and n > 0:
                vecs[norm(url)] = [x / n for x in v]
    return vecs, crawled


def tokens(text):
    words = [w for w in re.findall(r"[^\W_]+", text.lower()) if w not in STOP and not w.isdigit()]
    return words + [f"{a} {b}" for a, b in zip(words, words[1:])]


def load_texts(path):
    csv.field_size_limit(sys.maxsize)
    out = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            url = pick(row, "URL", "Address")
            text = pick(row, "Text", "Content", "Main_Text")
            if url and text:
                out[norm(url)] = Counter(tokens(text))
    return out


def tfidf_pairs(docs, max_df, min_sim, need):
    """TF-IDF fitted over every page in docs; returns pairs that touch a page in need."""
    n = len(docs)
    df = Counter()
    for tf in docs.values():
        df.update(tf.keys())
    if n >= MIN_DOCS_FOR_MAX_DF:
        keep = {t for t, d in df.items() if d / n <= max_df}
    else:
        keep = set(df)
    weights = {}
    for url, tf in docs.items():
        w = {t: c * (math.log((1 + n) / (1 + df[t])) + 1) for t, c in tf.items() if t in keep}
        length = math.sqrt(sum(x * x for x in w.values()))
        weights[url] = {t: x / length for t, x in w.items()} if length else {}
    postings = defaultdict(list)
    for url, w in weights.items():
        for t, x in w.items():
            postings[t].append((url, x))
    dots = defaultdict(float)
    for plist in postings.values():
        for i in range(len(plist)):
            ui, xi = plist[i]
            for uj, xj in plist[i + 1:]:
                key = (ui, uj) if ui < uj else (uj, ui)
                dots[key] += xi * xj
    return [(a, b, s) for (a, b), s in dots.items() if s >= min_sim and (a in need or b in need)]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--vectors")
    ap.add_argument("--vector-column", default=DEFAULT_VECTOR_COLUMN)
    ap.add_argument("--texts")
    ap.add_argument("--out", default="similarity.csv")
    ap.add_argument("--min", type=float, default=0.70, help="lowest similarity to write (default 0.70)")
    ap.add_argument("--max-df", type=float, default=0.5, help="drop text terms on more than this share of pages")
    args = ap.parse_args()
    if not (args.vectors or args.texts):
        ap.error("give --vectors, --texts or both")

    rows = []
    vecs, crawled = {}, set()
    if args.vectors:
        vecs, crawled = load_vectors(args.vectors, args.vector_column)
        print(f"vector coverage: {len(vecs)}/{len(crawled)} pages have an embedding vector")
        urls = sorted(vecs)
        for i, a in enumerate(urls):
            va = vecs[a]
            for b in urls[i + 1:]:
                s = sum(x * y for x, y in zip(va, vecs[b]))
                if s >= args.min:
                    rows.append((a, b, round(s, 4), "embedding"))
    if args.texts:
        docs = load_texts(args.texts)
        need = set(docs) - set(vecs)
        print(f"text similarity for {len(need)} page(s) without a vector, compared with all "
              f"{len(docs)} pages of text")
        no_text = sorted((crawled - set(vecs)) - set(docs))
        if no_text:
            print(f"WARNING: {len(no_text)} page(s) have neither a vector nor text and get no score, e.g. {no_text[0]}")
        missing_neighbours = set(vecs) - set(docs)
        if need and missing_neighbours:
            print(f"WARNING: {len(missing_neighbours)} page(s) with a vector have no text, so pages without a "
                  "vector cannot be compared with them; add their main text to --texts")
        if len(docs) < MIN_DOCS_FOR_MAX_DF:
            print(f"WARNING: only {len(docs)} pages of text (under {MIN_DOCS_FOR_MAX_DF}); --max-df not applied "
                  "and text scores are rough: check these pairs by reading them")
        if need and len(docs) < 2:
            print("WARNING: no other page text to compare with; no text pairs written")
        elif need:
            for a, b, s in tfidf_pairs(docs, args.max_df, args.min, need):
                rows.append((a, b, round(s, 4), "text"))

    rows.sort(key=lambda r: -r[2])
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["url_a", "url_b", "similarity", "method"])
        w.writerows(rows)
    print(f"{len(rows)} pairs at or above {args.min} -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
