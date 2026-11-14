#!/usr/bin/env python3
"""RECONCILIATION GATE - run before any deliverable ships.

Answers one question with a number, not an impression: is every keyword and every prompt we
researched accounted for somewhere in the final map?

It is easy to lose rows silently. A keyword folds into a head and the variant disappears from
view; a prompt is cut for scope and nobody records why; a prompt cluster merges into a keyword
page and its members stop being counted. Each of those is defensible on its own and indefensible
in aggregate, because the client counts rows. This gate makes every input land in exactly one of
three buckets - MAPPED, FOLDED or EXCLUDED-WITH-A-REASON - and fails if anything lands nowhere.

Inputs (paths are CLI args so it is portable):
  --keywords  final keyword list json: [{term, variant_list:[...]}, ...]
  --kw-map    keyword page_map.csv     (prompt_id,prompt,page,...)
  --prompts   prompt universe json:    {"full":[{prompt,...}], "cuts":[{prompt,cut_reason}]}
  --pr-map    prompt page_map.csv
  --unified   unified page universe json: [{page, kw, pr, origin}, ...]
Exit 0 only when every bucket reconciles.
"""
import json, csv, argparse, sys, collections

def main():
    a = argparse.ArgumentParser()
    for f in ('keywords', 'kw-map', 'prompts', 'pr-map', 'unified'):
        a.add_argument('--' + f, required=True)
    o = a.parse_args()
    fail = []

    kl = json.load(open(o.keywords))
    heads = {k['term'].strip() for k in kl}
    variants = [v for k in kl for v in (k.get('variant_list') or [])]
    kmap = list(csv.DictReader(open(getattr(o, 'kw_map'))))
    mapped_k = {r['prompt'].strip() for r in kmap}

    missing = heads - mapped_k
    if missing:
        fail.append(f"{len(missing)} researched keywords reach no page: {sorted(missing)[:5]}")
    extra = mapped_k - heads
    if extra:
        fail.append(f"{len(extra)} keywords in the map were never researched: {sorted(extra)[:5]}")

    P = json.load(open(o.prompts))
    live = {x['prompt'].strip() for x in P.get('full', [])}
    cuts = {x['prompt'].strip(): x.get('cut_reason', '') for x in P.get('cuts', [])}
    unreasoned = [p for p, why in cuts.items() if not str(why).strip()]
    if unreasoned:
        fail.append(f"{len(unreasoned)} prompts were cut with no written reason: {unreasoned[:3]}")
    pmap = list(csv.DictReader(open(getattr(o, 'pr_map'))))
    pmast = {r['prompt_id']: r['prompt'].strip() for r in pmap}
    mapped_p = set(pmast.values())
    lost = live - mapped_p
    if lost:
        fail.append(f"{len(lost)} live prompts reach no page: {sorted(lost)[:5]}")
    overlap = live & set(cuts)
    if overlap:
        fail.append(f"{len(overlap)} prompts are both live and cut: {sorted(overlap)[:3]}")

    U = json.load(open(o.unified))
    ukw = sum(r.get('kw', 0) for r in U)
    upr = sum(r.get('pr', 0) for r in U)
    if ukw != len(heads):
        fail.append(f"unified map counts {ukw} keywords, the research produced {len(heads)}")
    if upr != len(live):
        fail.append(f"unified map counts {upr} prompts, the universe holds {len(live)}")
    kpages = {r['page'] for r in kmap}
    upages = {r['page'] for r in U}
    gone = kpages - upages
    if gone:
        fail.append(f"{len(gone)} keyword pages vanished from the unified map: {sorted(gone)[:5]}")

    print("RECONCILIATION")
    print(f"  keywords researched   : {len(heads)} heads + {len(variants)} folded variants "
          f"= {len(heads) + len(variants)} total")
    print(f"  keyword heads mapped  : {len(heads & mapped_k)}")
    print(f"  variants              : folded into their head's page by design")
    print(f"  prompts authored      : {len(live) + len(cuts)}")
    print(f"  prompts live + mapped : {len(live & mapped_p)}")
    print(f"  prompts cut, reasoned : {len(cuts) - len(unreasoned)} of {len(cuts)}")
    print(f"  unified pages         : {len(U)}  ({ukw} keywords, {upr} prompts)")
    if fail:
        print("\nFAILURES:")
        for f in fail:
            print("  -", f)
        sys.exit(1)
    print("\nRECONCILIATION GATE: PASS - every researched keyword and prompt is accounted for")

if __name__ == '__main__':
    main()
