# Navigation and URLs for industries pages

Count these on the client set (`CLIENT_NAV` in `data/benchmark.py`), never on the cross-industry set. The rules
below are the defaults the counts usually support; state the client-set counts behind each one in the doc.

## Menu
- **Under Solutions, as a By industry group**, is the most common placement in B2B menus. Whatever the parent,
  keep its own landing page reachable on touch screens when it becomes a dropdown (a first item that links it is
  one way).
- **A top-level Industries item** suits long lists. Companies that give industries their own top-level item tend to
  list a dozen or more. Below about ten launch industries, keep them inside Solutions.
- **Link the overview page from the menu**: end the By industry group with "All industries". Many menus link only
  the individual industries, which leaves the overview page orphaned.
- **One label per thing**: the menu, the overview page and the footer use the same industry names in the same order.
  Menus and overview pages that list different industries are a common, avoidable inconsistency.

## Footer
- An **Industries group** with the same pages as the menu plus "All industries". New industries join the menu, the
  cards, the coverage line and the footer in the same release.

## URLs
- `/industries` for the overview page and `/industries/<industry>` for each industry page, with plain slugs
  (`education`, `energy`, `media`). Keyword-stuffed slugs (`/industries/<product>-for-<industry>`)
  read as spam, drift out of step with the names, and are hard to keep consistent.
- Segment pages nest under their industry (`/industries/energy/renewables`) once each segment has its own
  page.
- **The parent address must be live on launch day.** `/industries` publishes the same day as the first industry
  page, returns 200 and links every live industry page. A 404, an empty shell, a placeholder template or a redirect
  to the homepage at the parent address is one of the most common faults on industries sections.
- No placeholder or draft page on any crawlable address. A drafted industry page publishes into the template on
  launch day, or waits as a draft.
- If industry pages already live under another parent (a solutions or use-case path), move each to
  `/industries/<slug>` with one 301, merge pages that serve the same buyers, and update internal links rather than
  relying on the redirects.

## Page titles and descriptions
- Overview title under 60 characters, naming the category and "industries" (for example
  "Industry <Category> Solutions | <Brand>").
- Industry page title under 60 characters, leading with the industry's search term ("<Industry> <Category> |
  <Brand>").
- Meta descriptions: unique per page, naming the industries (overview) or the buyer types (industry page) and the
  offer. Follow the client's house length rule if it has one; otherwise 120 to 155 characters.

## Internal links
- Each industry page links to `/industries` and to two sibling industries in its closing band.
- Every blog post, report and event tagged to an industry links that industry page.
- The overview's answer blocks link their industry pages with descriptive anchors ("Explore energy").
- Breadcrumbs on both pages (Home > Industries > <Industry>) with BreadcrumbList markup.
