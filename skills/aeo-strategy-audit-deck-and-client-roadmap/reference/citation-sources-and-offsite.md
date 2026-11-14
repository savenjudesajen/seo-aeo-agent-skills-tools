# Citation-source analysis and the off-site plays

## The question

When an AI engine answers the tracked prompts, WHERE does it pull from? That list tells you where the
client needs to show up.

## Method

For the tracked prompt set, collect every retrieved source domain and compute:
- **Retrieved %:** the share of all retrievals that domain accounts for.
- **Cite rate:** how often a retrieval turns into an actual citation in the answer. This is the important
  one.

Then classify each domain: competitor site / UGC video / UGC community / editorial (trade press, news) /
analyst / review site / the client's own site.

## The pattern to look for

The table layout, one row per source domain, sorted by retrieved %:

| Source | Type | Retrieved | Cite rate | Client present? |
|---|---|---|---|---|
| source.example.com | one of the types above | M% | R | yes / no, verified live |

Questions to test:
1. **What share of retrievals comes from UGC, editorial or analyst sources** rather than vendor sites?
2. **Which source types get cited at a higher rate than competitor sites when retrieved?** Where earned
   sources convert better than vendor sites, being on the vendor site is table stakes and the earned layer
   is where the gains are.

A near-zero cite rate on a high-retrieval domain is a gap, not a dead end: the engine is reaching for that
source type and finding nothing citable from anyone.

Cross-check against the audience research: a site that is both high-affinity for the audience and cited
by AI is a top-priority placement.

## The off-site plays (rank them from the table above)

- **Video:** an expert explainer series on the glossary topics, cut into short clips, with question-form
   titles that mirror the tracked prompts exactly. Transcripts feed the content cycle. Highest leverage
   when the client has no webinars to repurpose yet (then it is a create-from-scratch motion; say so).
- **Community:** genuine expert answers in the communities where buyers actually ask. Not marketing. A
   real practitioner bench is an unfair advantage here.
- **Editorial and analyst:** analyst briefings, contributed articles to the trade press that already gets
   cited, and inclusion in "best of" listicles.

## Measurement

Off-site is measured like everything else: the tracked prompt set re-runs on a cadence, and community,
video and editorial moves should show up as visibility and citation gains within weeks. Don't treat
off-site as unmeasurable brand work.
