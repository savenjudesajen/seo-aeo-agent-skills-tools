# robots.txt rules and gotchas

Contents: How parsers actually read the file (RFC 9309, Google) · Worked example: an invented store · Platform notes · A healthy single-group file · Pagination and archive blocks · Ownership signals · WordPress specifics · Legacy rules · Host variants and who serves the file

## How parsers actually read the file (RFC 9309, Google)
- A crawler picks ONE group: the one whose user-agent line most specifically matches its
  product token. If none matches, it uses `User-agent: *`. Groups are never merged.
- Consecutive `User-agent:` lines share the rule block beneath them. That is how to give
  several bots the same rules without repeating the block per bot.
- Within a group the longest matching path wins; on a tie, Allow wins. `*` matches any
  run of characters, `$` anchors the end. Paths should start with `/`.
- The user-agent value is the product token only. A value with a version such as
  `PerplexityBot/1.0` will not match the crawler.
- A group with no Disallow lines (crawl-delay only, or Allow only) allows everything.
- Crawl-delay is ignored by Googlebot and Amazonbot. Anthropic honors it.
- robots.txt controls crawling, not indexing.

## Worked example: an invented store
The file below is made up to show the common mistakes together; it is not taken from any
site. `store.example.com` is a custom-built shop:

```
User-agent: *
Disallow: /cart/
Disallow: /checkout/
Disallow: /account/
Disallow: /search?
Disallow: /*?color=
Disallow: /*?sort=
Disallow: /static/
Disallow: /locations/
Disallow: *?sessionid=

# AI crawlers
User-agent: CCBot
User-agent: GPTBot
User-agent: Google-Extended
Allow: /
Disallow: /cart/

User-agent: OAI-SearchBot
User-agent: PerplexityBot/1.0
Allow: /

User-agent: Bytespider
Crawl-delay: 5

User-agent: facebookexternalhit
Allow: /

Sitemap: https://store.example.com/sitemap.xml
```

What it does well: the `*` group keeps cart, checkout, account, internal search and the
filter parameters out of every index; no search crawler is blocked from content pages; the
sitemap is declared on the canonical host.

What it gets wrong, and the lesson each one teaches:
1. **Training bots get more access than search bots.** CCBot, GPTBot and Google-Extended
   are named and opened, while Claude-SearchBot, Claude-User, ChatGPT-User, Googlebot and
   Bingbot fall to the stricter `*` group. That is the reverse of the AEO priority. Decide
   the training tokens separately (they are the client's choice) and never give them more
   than the search tokens.
2. **A factual page blocked only for the `*` bots.** `/locations/` carries the
   addresses and opening hours AI answers quote. The `*` bots (including Googlebot and the
   Claude search and user agents) cannot fetch it, while the named training group can.
   Unblock factual pages (locations, contact, shipping, returns, specifications) for
   everyone.
3. **Group isolation.** The named groups repeat none or almost none of the `*` disallows,
   so cart, checkout, account, search and filter URLs are open to OAI-SearchBot and the training
   bots. Fix: one shared block (several User-agent lines over a full copy of the `*` rules)
   or no AI groups at all.
4. **A versioned token.** `PerplexityBot/1.0` never matches, so PerplexityBot silently falls
   to `*`. Use the bare product token.
5. **Crawl-delay-only groups open the whole site** to that bot, because a group with no
   Disallow lines allows everything. A crawl-delay group for Googlebot or Amazonbot would
   also do nothing for load, since both ignore Crawl-delay.
6. **Allow-only groups** (here facebookexternalhit) open checkout and account paths to that bot.
7. **Render resources blocked.** `/static/` holds the CSS and JS bundles. Check in
   Search Console URL Inspection that Googlebot can render the page; if not, allow the
   folder.
8. **A path starting with `*`** instead of `/` (`*?sessionid=`) works in Google, not
   everywhere.

The checker reports points 3, 4, 5, 6 and 8 directly. Points 1, 2 and 7 come from reading
its per-token blocked-paths table, so always pass the contact or locations page, a product
or specification page and a static asset path in `--paths`.

## Platform notes
- **Commerce platforms** (Adobe Commerce/Magento, BigCommerce, Salesforce Commerce Cloud and
  others) serve CSS, JS and images from a platform static path. A rule blocking it hides
  render resources; check rendering before you accept it. Filter and sort parameters on
  category pages are the usual facet rules.
- **Shopify:** the default robots.txt is managed by the platform and edited through a
  `robots.txt.liquid` template; propose changes there, not as an uploaded file.
- **HubSpot, Webflow:** robots.txt is edited in the site settings; check who on the client
  side owns that setting.

## A healthy single-group file
A typical marketing site: one `User-agent: *` group disallowing internal search and the
admin or preview paths, plus the Sitemap line. No bot is named, so every AI search,
user-fetch and training token reads every content page and there is no isolation risk.
Report it as healthy. If named AI groups are ever added, each must repeat the `*` disallows.

The checker adds a LOW "no AI crawler is named" note on such files. It is a documentation
point, not a defect; do not let it outrank real findings.

## Pagination and archive blocks
If robots.txt blocks paginated archives (`/blog/page/`, `/news/page/`) or tag archives,
older posts are reached only through the sitemap and in-body links. Every post then needs a
link from a hub or category page, or it becomes hard to discover.

## Ownership signals
Typos in paths, duplicated rules and sitemaps listed more than once are harmless on their
own but usually mean nobody owns the file. Name an owner in the deliverable.

## WordPress specifics
- WordPress serves a virtual robots.txt (`Disallow: /wp-admin/`, `Allow:
  /wp-admin/admin-ajax.php`, the sitemap). A physical file in the web root replaces it
  entirely, so those defaults disappear unless they are copied in.
- Yoast and Rank Math can edit the file; check which one owns it before proposing edits.
- Do not block `/wp-content/` or `/wp-includes/`: themes serve CSS and JS from there.
- A dev or staging path in robots (for example `/staging/`) advertises it. Protect it with a
  password or noindex; a Disallow alone is not protection.

## Legacy rules
A rule that blocks an old static path (a previous site version, an archived microsite) is
worth checking: if those URLs now 301 to live pages, the block stops crawlers from seeing the
redirect, so the old links never consolidate. If they 404 or are gone, the line is dead
weight and can go. Fetch three or four of the blocked paths before you recommend either.

## Host variants and who serves the file
Fetch robots.txt on www, non-www, http and every subdomain. Each host has its own file, and
the Sitemap line should point at the canonical host. If two variants return different files,
find out why before you edit: a CDN or edge worker may rewrite robots.txt, a staging rule may
have leaked to production, or a plugin may regenerate the file. Fix it at the source that
actually serves it.
