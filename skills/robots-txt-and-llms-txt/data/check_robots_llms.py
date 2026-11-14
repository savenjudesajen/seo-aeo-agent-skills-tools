#!/usr/bin/env python3
"""Gate for the robots.txt + llms.txt skill. Python 3 standard library only; runs offline.

Reads a robots.txt and/or an llms.txt from local files you fetched yourself, and reports
what each AI crawler is actually allowed to do. It does not fetch anything.

    python3 check_robots_llms.py --robots robots.txt [--llms llms.txt] \
        [--paths / /services/ /blog/ /contact/ /cart/] [--json out.json] [--ban-dashes]

    python3 check_robots_llms.py --llms competitor-llms.txt      # llms.txt only

Exit 0 = no HIGH findings. Exit 1 = at least one HIGH finding. Exit 2 = usage error or a
robots file with no groups. It prints what it examined (groups, rules, tokens, paths) so a
clean run cannot be confused with a run that read nothing.
"""
import argparse
import json
import re
import sys

AI_TOKENS = {
    # token: (vendor, role). Roles starting with "search" or "user-triggered" must stay
    # crawlable for AEO; a block on / for them is a HIGH finding.
    "GPTBot": ("OpenAI", "training"),
    "OAI-SearchBot": ("OpenAI", "search index (ChatGPT search)"),
    "ChatGPT-User": ("OpenAI", "user-triggered fetch"),
    "ClaudeBot": ("Anthropic", "training"),
    "Claude-SearchBot": ("Anthropic", "search index"),
    "Claude-User": ("Anthropic", "user-triggered fetch"),
    "PerplexityBot": ("Perplexity", "search index"),
    "Perplexity-User": ("Perplexity", "user-triggered fetch"),
    "Google-Extended": ("Google", "control token: Gemini training and grounding"),
    "Googlebot": ("Google", "search, AI Overviews, AI Mode"),
    "Bingbot": ("Microsoft", "search, Copilot grounding"),
    "Applebot": ("Apple", "search (Siri, Spotlight)"),
    "Applebot-Extended": ("Apple", "control token: training opt-out"),
    "CCBot": ("Common Crawl", "open dataset, widely used for training"),
    "meta-externalagent": ("Meta", "training and indexing"),
    "meta-webindexer": ("Meta", "search (Meta AI)"),
    "Amzn-SearchBot": ("Amazon", "search (Alexa)"),
    "Amazonbot": ("Amazon", "general, may train"),
    "Bytespider": ("ByteDance", "search and training"),
}
SEARCH_ROLES = ("search", "user-triggered")
NO_CRAWL_DELAY = ("googlebot", "amazonbot")


def parse_robots(text):
    groups, cur, last_was_ua = [], None, False
    sitemaps, issues = [], []
    for n, raw in enumerate(text.lstrip("﻿").splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, val = [x.strip() for x in line.split(":", 1)]
        k = key.lower()
        if k == "user-agent":
            if not last_was_ua or cur is None:
                cur = {"agents": [], "rules": [], "crawl_delay": None, "line": n}
                groups.append(cur)
            cur["agents"].append(val)
            if "/" in val and val != "*":
                issues.append(("MEDIUM", "line %d: user-agent '%s' carries a version; use the product token only, it never matches" % (n, val)))
            last_was_ua = True
            continue
        last_was_ua = False
        if k == "sitemap":
            sitemaps.append(val)
            continue
        if cur is None:
            issues.append(("MEDIUM", "line %d: rule before any user-agent line" % n))
            continue
        if k in ("allow", "disallow"):
            if val and not val.startswith("/") and not val.startswith("*"):
                issues.append(("LOW", "line %d: path '%s' does not start with / (non-Google parsers may skip it)" % (n, val)))
            elif val.startswith("*"):
                issues.append(("LOW", "line %d: path '%s' starts with * not / (RFC 9309 expects /)" % (n, val)))
            cur["rules"].append((k, val))
        elif k == "crawl-delay":
            cur["crawl_delay"] = val
    return groups, sitemaps, issues


def group_for(groups, token):
    """The group a crawler obeys: the longest user-agent value its token starts with, else *."""
    t = token.lower()
    best, best_len = None, -1
    for g in groups:
        for a in g["agents"]:
            al = a.lower()  # a versioned value (Token/1.0) is not stripped: it does not match the bare token
            if al != "*" and t.startswith(al) and len(al) > best_len:
                best, best_len = g, len(al)
    if best:
        return best, "named"
    for g in groups:
        if any(a == "*" for a in g["agents"]):
            return g, "*"
    return None, "none"


def rule_to_re(path):
    esc = re.escape(path).replace(r"\*", ".*")
    if esc.endswith(r"\$"):
        esc = esc[:-2] + "$"
    return re.compile("^" + esc)


def allowed(group, path):
    """(allowed?, deciding rule). Longest match wins; on a tie Allow wins; empty Disallow allows all."""
    if group is None:
        return True, None
    best = None
    for kind, val in group["rules"]:
        if val == "":
            continue
        if rule_to_re(val).match(path):
            length = len(val)
            if best is None or length > best[0] or (length == best[0] and kind == "allow"):
                best = (length, kind, val)
    if best is None:
        return True, None
    return best[1] == "allow", "%s: %s" % (best[1].capitalize(), best[2])


def check_llms(text, ban_dashes=False):
    out = []
    lines = [ln.rstrip() for ln in text.lstrip("﻿").splitlines()]
    body = [ln for ln in lines if ln.strip()]
    if not body:
        return [("HIGH", "llms.txt is empty")], {}
    low = text.lower()
    if "<html" in low or "<!doctype" in low:
        return [("HIGH", "llms.txt returns an HTML page (a 404 template or soft 404), not Markdown")], {}
    if not body[0].startswith("# "):
        out.append(("HIGH", "first non-empty line is not an H1 ('# Name'), the only required element"))
    h1s = [ln for ln in body if re.match(r"^# ", ln)]
    if len(h1s) > 1:
        out.append(("MEDIUM", "%d H1s: this reads as a concatenated full-content dump; move it to llms-full.txt and keep llms.txt an index" % len(h1s)))
    if not any(ln.startswith(">") for ln in body[1:4]):
        out.append(("MEDIUM", "no blockquote summary right after the H1"))
    h2 = [ln[3:].strip() for ln in body if ln.startswith("## ")]
    links = re.findall(r"^\s*-\s*\[([^\]]+)\]\(([^)]+)\)(.*)$", text, re.M)
    if not h2:
        out.append(("MEDIUM", "no H2 sections grouping the links"))
    if not links:
        out.append(("HIGH", "no '- [name](url)' link lines"))
    nodesc = [u for _, u, rest in links if not rest.strip().startswith(":")]
    if links and len(nodesc) / len(links) > 0.3:
        out.append(("LOW", "%d of %d links have no ': description'" % (len(nodesc), len(links))))
    rel = [u for _, u, _ in links if not u.startswith("http")]
    if rel:
        out.append(("LOW", "%d relative link(s); use absolute URLs" % len(rel)))
    if "Optional" in h2 and h2[-1] != "Optional":
        out.append(("LOW", "## Optional is not the last section; agents skip from Optional onward"))
    if re.search(r"&amp;|&quot;|&#\d+;", text):
        out.append(("LOW", "unescaped HTML entities in the Markdown"))
    if re.search(r"<[^>]+>", text) and not re.search(r"<html|<!doctype", low):
        out.append(("LOW", "HTML or MDX tags left in the Markdown"))
    if ban_dashes and re.search("[\u2014\u2013]", text):
        out.append(("LOW", "em or en dash present (optional style check)"))
    urls = [u for _, u, _ in links]
    dup = {u for u in urls if urls.count(u) > 1}
    if dup:
        out.append(("LOW", "duplicate link targets: %s" % sorted(dup)[:5]))
    return out, {"h1": h1s[:1], "h2": h2, "links": len(links), "chars": len(text)}


def check_robots(text, paths, issues):
    groups, sitemaps, parse_issues = parse_robots(text)
    issues += parse_issues
    if not groups:
        return None
    star = next((g for g in groups if "*" in g["agents"]), None)
    star_dis = {v for k, v in (star["rules"] if star else []) if k == "disallow" and v}
    report = {"groups": len(groups), "rules": sum(len(g["rules"]) for g in groups),
              "sitemaps": sitemaps, "tokens": {}}
    # Group isolation: a named group never inherits the * rules.
    for g in groups:
        if "*" in g["agents"]:
            continue
        dis = {v for k, v in g["rules"] if k == "disallow" and v}
        if "/" in dis and not any(k == "allow" for k, _ in g["rules"]):
            continue  # a full block already covers every * disallow
        missing = star_dis - dis
        if star_dis and missing:
            sev = "HIGH" if len(missing) >= max(3, len(star_dis) // 2) else "MEDIUM"
            if not g["rules"]:
                why = "crawl-delay only" if g["crawl_delay"] else "no rules"
            elif not dis:
                why = "allow-only group"
            else:
                why = "named group"
            issues.append((sev, "group %s (%s) does not repeat %d of the * disallows, so those rules do not apply to it (groups never merge with *). Examples: %s"
                           % ("/".join(g["agents"]), why, len(missing), sorted(missing)[:4])))
        if g["crawl_delay"] and any(x.lower().startswith(NO_CRAWL_DELAY) for x in g["agents"]):
            issues.append(("LOW", "crawl-delay set for %s, which ignores it" % "/".join(g["agents"])))
    if not sitemaps:
        issues.append(("MEDIUM", "no Sitemap: line"))
    named_ai = []
    for tok, (vendor, role) in AI_TOKENS.items():
        g, how = group_for(groups, tok)
        res = {}
        for p in paths:
            ok, rule = allowed(g, p)
            res[p] = "allowed" if ok else "blocked (%s)" % rule
        report["tokens"][tok] = {"vendor": vendor, "role": role, "group": how, "paths": res}
        if how == "named":
            named_ai.append(tok)
        if not allowed(g, "/")[0] and role.startswith(SEARCH_ROLES):
            issues.append(("HIGH", "%s (%s, %s) is blocked from / : the site cannot appear in that engine's answers" % (tok, vendor, role)))
    if not named_ai:
        issues.append(("LOW", "no AI crawler is named; every AI bot inherits *. Fine for visibility, but the policy is implicit, not documented"))
    return report


def main():
    ap = argparse.ArgumentParser(description="Resolve robots.txt groups for AI crawlers and check llms.txt (offline).")
    ap.add_argument("--robots", help="local copy of a robots.txt")
    ap.add_argument("--llms", help="local copy of an llms.txt")
    ap.add_argument("--paths", nargs="*", default=["/", "/blog/", "/services/", "/contact/", "/wp-admin/", "/cart/", "/search?q=x"])
    ap.add_argument("--json", help="write the full report to this file")
    ap.add_argument("--ban-dashes", action="store_true", help="flag em/en dashes in llms.txt (when the house style bans them)")
    a = ap.parse_args()
    if not a.robots and not a.llms:
        ap.error("give --robots, --llms or both")

    issues, report = [], {"files": {"robots": a.robots, "llms": a.llms}}
    examined = []
    if a.robots:
        with open(a.robots, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        rr = check_robots(text, a.paths, issues)
        if rr is None:
            print("FAIL: no user-agent groups parsed from %s" % a.robots)
            sys.exit(2)
        report["robots"] = rr
        examined.append("%d groups, %d rules, %d AI tokens, %d paths, sitemaps=%d" % (
            rr["groups"], rr["rules"], len(AI_TOKENS), len(a.paths), len(rr["sitemaps"])))
    if a.llms:
        with open(a.llms, encoding="utf-8", errors="replace") as fh:
            lt = fh.read()
        li, meta = check_llms(lt, ban_dashes=a.ban_dashes)
        report["llms"] = meta
        issues += [(s, "llms.txt: " + m) for s, m in li]
        examined.append("llms.txt checked (%s links, %s H2s)" % (meta.get("links", 0), len(meta.get("h2", []))))
    report["findings"] = [{"severity": s, "finding": m} for s, m in issues]

    print("examined: " + "; ".join(examined))
    if a.robots:
        print("%-20s %-12s %-6s %s" % ("token", "vendor", "group", "blocked paths"))
        for tok, r in report["robots"]["tokens"].items():
            blocked = [p for p, v in r["paths"].items() if v.startswith("blocked")]
            print("%-20s %-12s %-6s blocked: %s" % (tok, r["vendor"], r["group"], ", ".join(blocked) or "none"))
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    for f in sorted(report["findings"], key=lambda f: order[f["severity"]]):
        print("[%s] %s" % (f["severity"], f["finding"]))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=1)
    sys.exit(1 if any(f["severity"] == "HIGH" for f in report["findings"]) else 0)


if __name__ == "__main__":
    main()
