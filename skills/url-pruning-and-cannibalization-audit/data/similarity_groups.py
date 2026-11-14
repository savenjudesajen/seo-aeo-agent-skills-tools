#!/usr/bin/env python3
"""Group pages by text similarity.
Usage: python similarity_groups.py pages.ndjson live_urls.txt out_groups.tsv [--vectors internal.ndjson]
pages.ndjson: {"Address","content"} (visible text export). Prints validation numbers against embeddings when --vectors is given.
Needs numpy and scikit-learn. The carry-over check is in reference/similarity-grouping-and-merge-check.md section 5."""
import sys, json, re, collections, numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering

def main():
    a = sys.argv[1:]
    pages, live, out = a[0], [l.strip() for l in open(a[1]) if l.strip()], a[2]
    txt = {}
    for l in open(pages):
        r = json.loads(l); txt.setdefault(r['Address'], r['content'])
    U = [u for u in live if u in txt]
    lc = collections.Counter()
    for u in U:
        for ln in set(x.strip() for x in txt[u].split('\n') if x.strip()): lc[ln] += 1
    bp = {l for l, c in lc.items() if c >= max(8, int(0.04 * len(U)))}
    docs = [' '.join(x.strip() for x in txt[u].split('\n') if x.strip() and x.strip() not in bp) for u in U]
    X = TfidfVectorizer(sublinear_tf=True, stop_words='english', min_df=2, max_df=0.5, ngram_range=(1, 2)).fit_transform(docs)
    S = (X @ X.T).toarray(); np.fill_diagonal(S, 0)
    lab = AgglomerativeClustering(n_clusters=None, metric='precomputed', linkage='average', distance_threshold=0.70).fit(1 - S).labels_
    if '--vectors' in a:
        vec = {}
        for l in open(a[a.index('--vectors') + 1]):
            r = json.loads(l); v = r.get('Extract semantic embeddings from page')
            if v:
                try: vec[r['Address']] = np.array([float(x) for x in re.split(r'[,\s]+', v.strip('[] ')) if x])
                except ValueError: pass
        V = [u for u in U if u in vec]
        if len(V) > 5:
            M = np.array([vec[u] / np.linalg.norm(vec[u]) for u in V]); G = M @ M.T; np.fill_diagonal(G, -1)
            idx = {u: i for i, u in enumerate(U)}; ii = [idx[u] for u in V]; T = S[np.ix_(ii, ii)].copy(); np.fill_diagonal(T, -1)
            ov = [len(set(np.argsort(-G[i])[:5]) & set(np.argsort(-T[i])[:5])) / 5 for i in range(len(V))]
            print(f'pages with vectors {len(V)} of {len(U)}; top-5 neighbour overlap with embeddings {np.mean(ov):.2f} (chance about {5/len(V):.2f})')
    with open(out, 'w') as f:
        f.write('URL\tGroup\n')
        for u, l in zip(U, lab): f.write(f'{u}\tC{l}\n')
    print(f'{len(U)} pages with text of {len(live)} live; {len(set(lab))} clusters')

if __name__ == '__main__': main()
