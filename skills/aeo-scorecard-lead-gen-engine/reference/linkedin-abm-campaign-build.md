# LinkedIn ABM campaign: build it as a draft in Campaign Manager

Contents: Read this first: the audience math decides whether paid is worth it · Agree these with the client before building · The current hierarchy (LinkedIn renamed its levels) · Build order · Company targeting: match by domain, not by name · Browser-automation gotchas (this UI is fiddly) · The blocker you'll hit: Company Page posting permission · Creative and lead form (once unblocked) · Safety

Stand up the LinkedIn layer of the motion as a **draft** in LinkedIn Campaign Manager, using a
browser-automation tool in the user's own browser. There's no campaign-creation API without
LinkedIn's developer approval, but the campaign and ad set can be built in the UI. Build a draft
only: never launch (that commits spend) without explicit sign-off for that action.

## Read this first: the audience math decides whether paid is worth it
LinkedIn won't serve an audience under **about 300 members** (a hard floor) and **recommends about
50,000** for efficient delivery. For a list of small or niche firms this is harsh:
- one company, even a larger one in the list, may reach only a few hundred members;
- pooling every target company often lands in the hundreds or low thousands, far under the
  recommendation, with a high forecast cost per lead.

It will serve once above 300, but reach is thin and CPMs are high. **Agree this with the client up
front:** the outbound sequences (cold email plus CRM nurture) are the primary 1:1 channel; LinkedIn
paid is a supporting, awareness layer, so don't let them over-fund it. True 1:1 (one campaign per
company) is impossible on paid, since one company is far below 300: **pool all target companies into
one matched-company audience.**

## Agree these with the client before building
- **Objective:** Lead Gen Form (a native in-feed form; needs no landing page, best when the
  per-account pages aren't all deployed), Website visits (needs a live URL per ad) or Brand awareness.
- **Audience scope:** pool all companies (recommended), a pilot, or a subset.
- **Daily budget:** a small agreed test figure.
- Build as a **draft**; the client launches after review.

## The current hierarchy (LinkedIn renamed its levels)
**Campaign** (formerly *Campaign Group*; holds the objective and optional budget optimisation) →
**Ad set** (formerly *Campaign*; holds audience, budget, schedule, bidding and ad format) → **Ad**
(creative and lead form). The Create menu shows "Campaign" and "Ad set or ads". The objective is
chosen at the Campaign level.

## Build order
1. Accounts → open the client's ad account → **Create → Campaign**.
2. **Campaign:** name it; pick **Lead generation**; budget optimisation **off** (the budget lives on
   the ad set); a start date of today is fine for a draft → Next.
3. **Ad set:**
   - Name it; the objective is inherited.
   - Skip "What you're marketing" (an optional source URL) and dismiss the auto-targeting prompt.
   - **Locations:** the default is the account's home country. Remove it and add the client's real
     markets (keyboard method below).
   - **Profile language:** check LinkedIn's note beside the field before changing it. LinkedIn's note
     says English there targets members of every language in the chosen locations; it is not an
     English-only filter.
   - **Company targeting (the ABM core):** "Who is your target audience?" → Narrow → search → type a
     company; it builds a **Company Names (current jobs)** any-of group. Add each company.
   - **Uncheck "Enable Audience Expansion":** ABM must not bleed beyond the target companies.
   - Don't add an AND group (seniority, function) on a tiny audience; it only shrinks it.
   - **Ad format:** Single image (the default). **Budget and schedule:** the default daily budget is
     far above a test budget; change it to the agreed figure. **Optimisation:** Leads. **Bidding:**
     Maximum delivery.
   - Next → confirm the save (objective and format lock after saving; that's fine) → Save. The
     campaign now has an ID and persists as a draft.

## Company targeting: match by domain, not by name
Name search is ambiguous: a common company name returns many unrelated companies, and even full legal
names can fail to match. **The accurate method is a company-list matched audience uploaded by
domain:** build a CSV of `companyname, website, country` from the audited domains and upload it (the
ad set's list upload, or Assets → Matched Audiences). It matches by domain and takes about 24 to 48
hours to process. For the draft, seed a few cleanly matched companies to shape the audience and get a
real size estimate, then swap in the domain-matched list before launch.
- The company search clears and keeps focus after a successful pick. If a pick fails (no match), the
  text stays and the next typed name concatenates onto it ("No results"). Verify with the chip area
  and the audience-size number, not blind.

## Browser-automation gotchas (this UI is fiddly)
- **Close the sticky banners** at the top and bottom of the page: they hide the sticky Next/Previous
  footer and cover dropdowns.
- **Dropdowns render below the field**, often below the fold. Find the element and click it by its
  element reference rather than by coordinates, or scroll to free vertical space first.
- **Fast location entry by keyboard, no coordinates:** click the location search once, then for each
  country type the name, wait about 2 seconds, press Down, then Return. That selects the top result
  and clears and refocuses the field, so you can chain several countries in one batch of actions.
  Return alone doesn't select; you need Down, then Return.
- **Don't use select-all (Ctrl/Cmd+A) to clear a field.** If the field has lost focus, it selects the
  whole page, and the next keystrokes corrupt the form state (it can wipe the company filter or jump
  to another section). Use the field's clear (×) button, or the type → Down → Return pattern, which
  clears by itself. A triple-click on the field works when focus is certain.
- **Chips wrap to new rows as you add them**, shifting fixed coordinates: another reason to prefer
  the keyboard method. When you must click, take a fresh screenshot or find the element again.
- **Page scrolling can snap back to the top.** The reliable way to reach a section is to find the
  target element and scroll to its reference (this works for the daily-budget field and the
  audience-expansion checkbox). Clicks can target a reference too.

## The blocker you'll hit: Company Page posting permission
Building the ad creative or lead form shows "Permission required: creating or modifying ads requires
permissions granted by your company page admin." The ad account needs **Sponsored Content posting
rights on the client's LinkedIn Company Page**. The client fixes it: Page → Admin tools → Manage
admins → add the user or ad account as a Sponsored Content poster or paid-media admin, or approve a
"Request access". This is a permissions action: surface it to the user, don't click it yourself.
Until it's granted you can't build the form or creative, but the campaign and ad set still save as a
draft.

## Creative and lead form (once unblocked)
- **A pooled audience needs a generic creative.** Naming one company to an audience made of all of
  them is wrong. Keep the per-company creatives for the outbound 1:1 layer. A generic hook asks
  the viewer whether AI recommends them for their category, and offers a free scorecard.
  Upload the PNGs through the browser tool's file upload.
- **Lead Gen form:** offer "Get your AI search scorecard"; fields: first name, work email, company,
  job title. A **privacy-policy URL is mandatory**. Add a thank-you and delivery step.

## Safety
Build as a draft. Never click launch or publish (that commits spend). Requesting Page access,
granting permissions and changing account settings are the client's actions: surface them, don't
perform them.
