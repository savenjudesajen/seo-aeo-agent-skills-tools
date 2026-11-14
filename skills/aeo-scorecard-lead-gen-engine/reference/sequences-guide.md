# Sequences playbook: the outbound layer

The scorecard is the anchor. Cold outreach drives to it; the page converts; warm nurture picks up the
engagement signal and routes a booked meeting to sales.

```
Cold (email + LinkedIn) -> Scorecard landing page -> Warm nurture (CRM) -> Meeting -> Sales handoff
```

Same hook the whole way. If the ad, the email and the page tell three different stories, none of them
lands. Two paths run side by side: outbound to named contacts, and an inbound path for anyone who
engages with a scorecard page. If the client already has its own cadence and handoff rules, use
those and keep only the hook and the scorecard link from this playbook.

## Cold cadence: 7 touches over about three and a half weeks
A starting point; adjust the spacing to the client's sales cycle.

| # | Day | Channel | Purpose | Subject idea |
|---|---|---|---|---|
| 1 | 1 | Email | The scorecard link and one finding | a question about [category] for [Company] |
| 2 | 3 | Email | Show the receipt: one buyer question, who AI recommended | the answer AI gave your buyers |
| 3 | 6 | LinkedIn | Connect with a one-line note, no link | (note of 300 characters or fewer) |
| 4 | 10 | Email | Why it happens and why it's fixable | why [Competitor] gets recommended |
| 5 | 14 | Email | One practical fix they can make without you | one change for [Company]'s pages |
| 6 | 18 | LinkedIn | Short message; offer a 15-minute walkthrough | (two sentences) |
| 7 | 24 | Email | Polite close; the page stays live | leaving this with you |

Rules:
- One idea per email, under about 120 words. Lowercase subjects read like a person, not a campaign.
- Every email carries a specific fact about the recipient's company.
- Stop on a reply, opt-out, bounce or booking; on completion, route to long-term nurture.
- **The "why it happens" email (touch 4) usually does the most work:** separate classic search from
  AI answers (the pages can rank and still not be quotable), then show the fix. It respects the work
  they've done and makes the bad news solvable.

## Warm nurture: three triggers (CRM workflows)
| Workflow | Trigger | Emails | Exit |
|---|---|---|---|
| A: Engaged | Viewed the scorecard page, no form | +1 day: a soft nudge | To B on form submit |
| B: Requested | Submitted the form or requested the plan | Immediately: delivery; +2 days: the gated brief unlocked | Booked → handoff; else to C |
| C: High intent | Clicked to see the full plan or opened the delivery 2+ times | +4 days: proof; +8 days: the cost of waiting; +14 days: break-up | Booked → handoff; else long-term nurture |

**Handoff:** form submit → marketing-qualified lead. Meeting booked → sales-qualified lead: create the
deal and a task, and unenrol the contact from everything else. A reply to any cold step → pause the
cold sequence immediately and route to a person. Not in the ideal customer profile, or a hard bounce
→ suppress.

## Personalisation
- **Single pilot account:** hardcode the real values (competitor, score, the receipt); leave only the
  recipient's first name and the sender as merge fields. It reads better than a template and can't
  fail a merge.
- **Many accounts:** every merge field maps to a master-sheet column, so the row that produced the
  scorecard also personalises the sequence.

## Where this stalls (platform limits)
Cold-email tools (e.g. Instantly) and CRMs (e.g. HubSpot) often have no connector wired. Deliver the
campaign as **structured copy + an import-ready file (JSON campaign + leads CSV) + a workflow spec**,
so it loads by hand in minutes. Don't block the whole build on an integration. Propagate the live
landing URL into every email once the page is deployed.
