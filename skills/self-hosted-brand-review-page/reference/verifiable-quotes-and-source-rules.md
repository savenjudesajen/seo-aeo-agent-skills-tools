# Verifiable quotes: crawler facts, platform rules, markup and the quote card

Contents: 1. Why quote text must be in the server HTML · 2. Platform rules (who may quote what) · 3. FTC rules that shape the page (US) · 4. Structured data · 5. The quote card (HTML shape) · 6. Quote selection rules

Platform terms, crawler policies and search guidance change. Re-read each source named here
before each new client and note the date you checked.

## 1. Why quote text must be in the server HTML

- GPTBot, ClaudeBot and PerplexityBot fetch pages without running JavaScript (Vercel's study
  "The rise of the AI crawler", December 2024, found none of the major AI crawlers render JS).
  Googlebot and Gemini do render, later.
- So anything inside a JS widget (review-platform widgets, testimonial scripts, Reddit and X embed
  scripts, client-side rich-text add-ons, client-side tables) or inside an iframe is invisible to
  most AI crawlers.
- LinkedIn's robots.txt disallows `/embed/feed/update/` for Googlebot, so a LinkedIn iframe's text
  is not indexed as part of the host page either. https://www.linkedin.com/robots.txt
- Source pages AI tools would use to cross-check a quote have their own bot rules: some review
  platforms block AI training crawlers from individual review URLs while allowing search and
  user-triggered agents; Reddit blocks most crawlers other than Google; LinkedIn restricts
  automated access. Check each source's robots.txt. The page's own HTML is the primary evidence.
  The links let humans, and AI engines where allowed, check it.

Rule: every quote is verbatim text in the HTML, with a visible link to the original. An official
embed may sit under it for human readers. Never rely on the embed alone.

## 2. Platform rules (who may quote what)

| Platform | Quote review text? | Rules |
|---|---|---|
| G2 | Restricted: typically only on a paid plan and with the reviewer's opt-in | Backlink to the individual review. The aggregate star rating may be shown with a backlink to the profile and G2's source credit. Badges unaltered. Logo only under licence. Read G2's community guidelines and the free-profile service description at https://legal.g2.com before quoting any excerpt |
| Capterra, GetApp, Software Advice | Yes, free | Verbatim only, context kept, no paraphrase; link to the review; quotes must be under 12 months old; own-product reviews only; carry the exact disclaimer text from the current content policy (copy it from the policy page, do not retype it from memory). Video reviews: full YouTube embed, no custom start time, link back |
| TrustRadius | Only with an active licence | Cite TrustRadius and link to the original review; award badges free to use unaltered (see its branding page) |
| LinkedIn | Quote as you would any public statement | Public posts only offer "Embed this post". Asking the author is a courtesy, especially with a known creator. Link the post permalink |
| YouTube | Quote a transcript line | Link `watch?v=ID&t=SECONDSs`. Use the standard iframe (Google advises against relying on clicks to load video, so a click-to-load facade may hide the video from it). Skip VideoObject markup: a roundup is not a watch page |
| Reddit | Quote a comment | Link the comment permalink; the official embed is subject to Reddit's embed terms and is JS |
| Customer stories, webinars | Yes | Quote from the published story; disclose any material connection |

Quoting policy is the client's decision. Lay out the terms above, get the decision in writing,
record it in each row's `permission_note`, and keep the Capterra disclaimer and 12-month rotation
regardless of the policy chosen.

## 3. FTC rules that shape the page (US)

- 16 CFR Part 465 (Trade Regulation Rule on the Use of Consumer Reviews and Testimonials,
  effective October 2024). 465.6: do not present a site you control as independent reviews, so the
  page says plainly that the brand published it. 465.7(b): do not imply the displayed reviews are
  all or most of them when negatives were left out, so the page says it is a selection and links
  every full profile.
- Endorsement Guides (16 CFR Part 255): no editing that changes the meaning; an outcome quote can
  imply typical results, so qualify outcome numbers; carry over a platform's "incentivized" label.

## 4. Structured data

- No Review or AggregateRating markup about the brand on its own site. Google's review snippet
  guidelines: when an entity controls reviews about itself, its pages are ineligible for review
  stars, including reviews shown through an embedded third-party widget; and do not aggregate
  ratings from other sites.
  https://developers.google.com/search/docs/appearance/structured-data/review-snippet
- Use: `Article` or `BlogPosting` (author Person, publisher Organization, datePublished,
  dateModified, about the product with no rating) plus `citation`, one CreativeWork per quoted
  source (url, author, datePublished, publisher; `SocialMediaPosting` for LinkedIn and Reddit,
  `VideoObject` reference for YouTube). https://schema.org/citation
- Add the G2, Capterra, TrustRadius and Gartner Peer Insights profile URLs to the Organization's
  `sameAs` in the site's Organization markup.
  https://developers.google.com/search/docs/appearance/structured-data/organization
- schema.org `Quotation` is in the pending area with no Google feature. Optional.
- FAQPage markup no longer gives a rich result outside a narrow set of authoritative government
  and health sites. Use it only if the template already emits it, and check current guidance.

## 5. The quote card (HTML shape)

```html
<figure class="review-quote" id="q-<platform>-<yyyy-mm-dd>-<slug>">
  <blockquote cite="<review or post URL>">
    <p>Exact verbatim excerpt, context kept.</p>
  </blockquote>
  <figcaption>
    <span>Reviewer as the platform shows them</span>, <span>Role</span>, <span>Company or size</span>
    <span aria-label="Rated 4 out of 5">4/5</span>
    <a href="<review or post URL>"><cite>Review or post title</cite></a> on <span>Platform</span>,
    <time datetime="YYYY-MM-DD">Month D, YYYY</time>
    <span>Incentivized review</span><!-- only when the platform labels it -->
  </figcaption>
  <!-- optional official embed below, for human readers -->
</figure>
```

Attribution sits outside the blockquote (HTML spec). `<cite>` holds the title of the work, never
the person's name. If the CMS rich text cannot hold a figure or attributes, the minimum is a
native rich-text blockquote followed by a paragraph carrying name, role, platform, date and a
link. That minimum passes the gate.

## 6. Quote selection rules

- Verbatim only. Cut with an ellipsis, never reword. Keep the sentence that gives context.
- Each quote earns its place by saying something specific: a job done, a time saved, a named
  workflow. "Great tool!" is filler.
- Match the brand's current positioning. A glowing review that describes the product the brand
  used to be (an old category label) works against any narrative-correction work running in
  parallel. Skip it, or date it and pair it with what changed.
- Pushback is required: at least two negative or mixed quotes, taken from the complaints that
  recur on the platforms and in the competitor-written reviews on page one. Each gets a dated
  answer: what changed, or why the trade-off exists.
- Re-check every quote against the live source on publish day and at each refresh. Reviewers edit
  and delete reviews.
- Record every quote in the ledger (`data/quote_ledger_template.csv`) before it goes on the page.
