#!/usr/bin/env python3
"""Content alignment audit: draft clusters and strategies (standard library only, offline).

Joins a Search Console page export with a similarity-pairs export, clusters pages, and writes a draft
audit sheet in the columns of audit_output_template.csv. Strategies are DRAFTS: the agent must still
scrape the pages the skill names, measure the value-add ratio and review every row before the gate.

Usage:
    python run_audit.py --gsc gsc_pages.csv --pairs similarity.csv [--value-adds scrape.csv] \
        [--out draft_audit.csv] [--cluster-threshold 0.85] [--scrape-imp 5000] \
        [--consolidation-imp 10000] [--months 3]

Inputs
    --gsc         Columns URL (or Page / Top pages / Landing page), Impressions, Clicks, Position.
                  URL x query rows are aggregated to one row per URL (impression-weighted position).
    --pairs       A crawler "semantically similar" export (Address, Closest Semantically Similar Address,
                  Semantic Similarity Score), or url_a, url_b, similarity[, method] as written by
                  similarity_pairs.py. Text-based pairs (method = text) are noted on the row.
    --value-adds  Optional, filled after scraping: URL, Value_Add (0-1, measured as in the decision
                  matrix), Unique_Content (YES/NO/PARTIAL), Backlinks (count), Scrape_Summary.

Thresholds are defaults from the skill's decision matrix. --scrape-imp and --consolidation-imp are totals
over the export window: scale them together with the site's traffic. Set --months to the length of the
Search Console export; the per-month rules (RETIRE, REFORMAT, REFRESH) divide impressions by it.
"""

import argparse
import csv
import sys
from urllib.parse import unquote

COLUMNS = [
    "URL", "Impressions", "Clicks", "Position", "Cluster_ID", "Cluster_Leader", "Similarity_Score",
    "Value_Add", "Strategy", "Confidence", "Rationale", "Unique_Content", "Scrape_Summary",
    "GSC_Performance", "Research_Notes", "Action_Required", "Effort_Level",
]
EFFORT = {"REMAIN": "Zero", "RETIRE": "Very Low", "REDIRECT": "Low", "REFRESH": "Low",
          "REFORMAT": "Low-Medium", "REPURPOSE": "Medium"}


def norm(url):
    u = unquote((url or "").strip())
    if u.endswith("/") and u.count("/") > 3:
        u = u[:-1]
    return u


def num(value, default=0.0):
    try:
        return float(str(value).replace(",", "").replace("%", "").strip())
    except ValueError:
        return default


def pick(row, *names):
    lower = {k.strip().lower(): v for k, v in row.items() if k}
    for n in names:
        if n.lower() in lower:
            return lower[n.lower()]
    return None


def add_note(note, text):
    return (note + "; " if note else "") + text


def load_gsc(path):
    pages = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            url = pick(row, "URL", "Page", "Top pages", "Landing page", "Address")
            if not url:
                continue
            p = pages.setdefault(norm(url), {"imp": 0.0, "clk": 0.0, "pos_x_imp": 0.0, "pos_n": 0})
            imp = num(pick(row, "Impressions"))
            pos = num(pick(row, "Position", "Average position"))
            p["imp"] += imp
            p["clk"] += num(pick(row, "Clicks"))
            p["pos_x_imp"] += pos * (imp or 1)
            p["pos_n"] += imp or 1
    for p in pages.values():
        p["pos"] = round(p["pos_x_imp"] / p["pos_n"], 1) if p["pos_n"] else 0.0
    return pages


def load_pairs(path):
    sim, text_based = {}, set()
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            a = pick(row, "Address", "url_a")
            b = pick(row, "Closest Semantically Similar Address", "url_b")
            s = pick(row, "Semantic Similarity Score", "similarity")
            if not (a and b and s):
                continue
            a, b, s = norm(a), norm(b), num(s)
            sim.setdefault(a, {})[b] = max(s, sim.get(a, {}).get(b, 0.0))
            sim.setdefault(b, {})[a] = max(s, sim.get(b, {}).get(a, 0.0))
            if (pick(row, "method") or "").strip().lower() == "text":
                text_based.add(frozenset((a, b)))
    return sim, text_based


def load_value_adds(path):
    out = {}
    if not path:
        return out
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            url = pick(row, "URL")
            if url:
                va = pick(row, "Value_Add")
                out[norm(url)] = {
                    "va": num(va, None) if va not in (None, "") else None,
                    "unique": pick(row, "Unique_Content") or "",
                    "backlinks": num(pick(row, "Backlinks"), 0),
                    "summary": pick(row, "Scrape_Summary") or "",
                }
    return out


def cluster(pages, sim, threshold):
    order = sorted(pages, key=lambda u: -pages[u]["imp"])
    assigned, clusters = {}, []
    for u in order:
        if u in assigned:
            continue
        members = [u] + [v for v in order if v not in assigned and v != u
                         and sim.get(u, {}).get(v, 0.0) > threshold]
        if len(members) == 1:
            continue
        cid = f"cluster_{len(clusters) + 1}"
        for m in members:
            assigned[m] = cid
        clusters.append((cid, u, members))
    return assigned, clusters


def draft(page, leader, s, va, backlinks, args):
    """Return (strategy, confidence, rationale, note, leader_refresh) for a non-leader page vs its leader."""
    if va is None:
        return ("REMAIN", "LOW", "Value-add not measured; draft only",
                "Scrape this page and its leader, measure Value_Add, then re-run", False)
    m = args.months
    better = leader["imp"] > page["imp"] and leader["pos"] and page["pos"] - leader["pos"] >= 2
    if s >= 0.92 and va < 0.10 and page["imp"] / m < 50 and backlinks == 0:
        return "RETIRE", "HIGH", "Near-duplicate, negligible traffic, no backlinks", "", False
    if s >= 0.90 and va < 0.20 and better:
        conf = "LOW" if s < 0.92 or backlinks else "HIGH"
        note = "Has backlinks: plan the redirect" if backlinks else ""
        if max(page["imp"], leader["imp"]) > args.consolidation_imp:
            note = add_note(note, "Above the consolidation threshold: scrape both pages first")
            conf = "LOW" if conf == "LOW" else "MEDIUM"
        return "REDIRECT", conf, "High similarity, little unique content, leader performs better", note, False
    if s >= 0.85 and 0.30 <= va <= 0.70 and (page["imp"] + leader["imp"]) / m > 100:
        return ("REDIRECT", "MEDIUM", "Overlaps the leader; move its unique content into the leader first",
                "Leader drafted as REFRESH; check the leader's own value-add against this page", True)
    if 0.80 <= s <= 0.88 and page["imp"] / m > 50 and leader["imp"] / m > 50 and 0.40 <= va <= 0.70:
        return "REFORMAT", "MEDIUM", "Similar topic, both get traffic; differentiate the format", "", False
    if 0.70 <= s < 0.90 and 0.20 <= va <= 0.60:
        return ("REPURPOSE", "MEDIUM", "Similar but with unique content; rewrite for a distinct intent",
                "Check query overlap (< 30%) before rewriting", False)
    if s >= 0.88:
        return ("REDIRECT", "LOW", "Ambiguous: high similarity without a clear rule match",
                "Flag for manual review", False)
    return "REMAIN", "HIGH" if s < 0.70 or va > 0.60 else "MEDIUM", "Sufficiently distinct", "", False


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--gsc", required=True)
    ap.add_argument("--pairs", required=True)
    ap.add_argument("--value-adds")
    ap.add_argument("--out", default="draft_audit.csv")
    ap.add_argument("--cluster-threshold", type=float, default=0.85)
    ap.add_argument("--scrape-imp", "--high-imp", dest="scrape_imp", type=float, default=5000,
                    help="scrape threshold: pages above it need scrape findings")
    ap.add_argument("--consolidation-imp", type=float, default=10000,
                    help="consolidation threshold: scrape both pages before redirecting above it")
    ap.add_argument("--months", type=float, default=3, help="months covered by the Search Console export")
    args = ap.parse_args()

    pages = load_gsc(args.gsc)
    sim, text_based = load_pairs(args.pairs)
    vas = load_value_adds(args.value_adds)
    for u in sim:  # pages present in the crawl but absent from Search Console
        pages.setdefault(u, {"imp": 0.0, "clk": 0.0, "pos": 0.0})
    assigned, clusters = cluster(pages, sim, args.cluster_threshold)
    leaders = {cid: lead for cid, lead, _ in clusters}
    members = {cid: ms for cid, _, ms in clusters}

    drafts, refresh_leaders = {}, set()
    for u, p in pages.items():
        cid = assigned.get(u, "standalone")
        lead = leaders.get(cid)
        info = vas.get(u, {})
        if lead and lead != u:
            s = sim.get(u, {}).get(lead, 0.0)
            strat, conf, why, note, leader_refresh = draft(p, pages[lead], s, info.get("va"),
                                                           info.get("backlinks", 0), args)
            if leader_refresh:
                refresh_leaders.add(lead)
            perf = (f"{p['imp'] / pages[lead]['imp']:.0%} of leader impressions; position {p['pos']} vs "
                    f"{pages[lead]['pos']}") if pages[lead]["imp"] else ""
            if frozenset((u, lead)) in text_based:
                note = add_note(note, "Text-based similarity (TF-IDF): read against text bands")
            drafts[u] = (cid, False, s, strat, conf, why, note, perf)
        elif lead == u:
            s = max((sim.get(u, {}).get(v, 0.0) for v in members[cid] if v != u), default=0.0)
            drafts[u] = (cid, True, s, "REMAIN", "MEDIUM", "Cluster leader",
                         "Similarity is the highest score to a cluster member; check for REFRESH (dated) or "
                         "REFORMAT (poor structure) after the scrape", "Leader")
        else:
            nearest = max(sim.get(u, {}).items(), key=lambda kv: kv[1], default=(None, 0.0))
            s = nearest[1]
            note = "Nearest-neighbour score; check for REFRESH (dated) or REFORMAT (poor structure) after the scrape"
            if 0.70 <= s <= args.cluster_threshold:
                note = "Moderate overlap (0.70-0.85): repurpose candidate; " + note
            if nearest[0] and frozenset((u, nearest[0])) in text_based:
                note = add_note(note, "Text-based similarity (TF-IDF): read against text bands")
            drafts[u] = (cid, False, s, "REMAIN", "MEDIUM", "No neighbour above the cluster threshold", note, "")

    rows = []
    for u, (cid, is_leader, s, strat, conf, why, note, perf) in drafts.items():
        p, info = pages[u], vas.get(u, {})
        if u in refresh_leaders:
            strat, conf = "REFRESH", "MEDIUM"
            why = "Stronger page of an overlapping pair; absorb the sibling's unique content and update it"
            note = "Combined monthly impressions above 100; measure this page's value-add against the sibling"
        if strat in ("REDIRECT", "RETIRE") and info.get("backlinks") and "backlinks" not in note:
            note = add_note(note, "Has backlinks: plan the redirect")
        if p["imp"] > args.scrape_imp and not info.get("summary"):
            conf = "LOW"
            note = add_note(note, "Above the scrape threshold: scrape required")
        va = info.get("va")
        rows.append({
            "URL": u, "Impressions": int(p["imp"]), "Clicks": int(p["clk"]), "Position": p["pos"],
            "Cluster_ID": cid, "Cluster_Leader": str(is_leader).upper(), "Similarity_Score": round(s, 2),
            "Value_Add": round(va, 2) if va is not None else ("N/A" if is_leader else ""),
            "Strategy": strat, "Confidence": conf, "Rationale": why,
            "Unique_Content": info.get("unique") or ("N/A" if is_leader else ""),
            "Scrape_Summary": info.get("summary", ""), "GSC_Performance": perf, "Research_Notes": note,
            "Action_Required": str(strat != "REMAIN" or conf == "LOW").upper(),
            "Effort_Level": EFFORT[strat],
        })

    rows.sort(key=lambda r: (r["Cluster_ID"] == "standalone", r["Cluster_ID"], -r["Impressions"],
                             r["Action_Required"] != "TRUE"))
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)

    counts = {}
    for r in rows:
        counts[r["Strategy"]] = counts.get(r["Strategy"], 0) + 1
    print(f"{len(rows)} pages, {len(clusters)} clusters -> {args.out}")
    for k in sorted(counts):
        print(f"  {k}: {counts[k]}")
    print("Drafts only: scrape, measure value-adds, review every row, then run verify_audit_output.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
