# Section types: industries overview and industry pages (45 types)

One taxonomy for both pages. Every section type seen on the starter cross-industry set: 12 companies in cloud,
enterprise software, consulting and IT services, one overview page and one industry page each (the same industry
for every company). The codings live in `data/benchmark.py` (`TYPES`). This table mirrors that file: change the
script first, then update the table from its output.

How to use it:
- Reuse these codings for any client. Re-code the client's own set (competitors and category leaders) against the
  same ids in `CLIENT_HUBS` and `CLIENT_IND`, so every count reads "client set + cross-industry = all".
- Every type lands somewhere in the client's block model or gets a "Not used" line with a reason. The Lands column
  is the default; change it per client and say why.
- A type counts only where the page itself showed it. A site-wide launcher (chat, assistant) is a site feature, not
  a section.
- Best-example notes describe what the page does. Re-read the live page before you quote anything from it.

| id | Section type | Overview pages (of 12) | Industry pages (of 12) | Overview pages with it | Industry pages with it | Best example | Lands (default) |
|---|---|---|---|---|---|---|---|
| 1 | Hero (H1, one-line promise, button) | 12 | 12 | all 12 | all 12 | SAP (industry page): the line under the H1 names the four buyer types the page serves | Hero (both pages) |
| 2 | Announcement banner (event, report, news) | 2 | 3 | Microsoft, IBM | Microsoft, IBM, SAP | IBM (overview page): runs its newest flagship report as a site banner with one headline figure | Announcement banner (site-wide) |
| 3 | In-page navigation (jump links, sticky local menu, index, breadcrumb, filters, tabs) | 8 | 9 | Microsoft, IBM, Oracle, SAP, Accenture, PwC, Capgemini, Cognizant | AWS, IBM, Oracle, SAP, Adobe, Accenture, PwC, Capgemini, Cognizant | PwC (industry page): puts an index of six anchor links beside the H1 | Jump navigation (both pages) |
| 4 | Industry list without descriptions | 3 | 0 | Oracle, SAP, Capgemini | none | Oracle (overview page): an A to Z list of about twenty industry links, nothing else per item | Industry directory (each entry carries a line instead) |
| 5 | Industry cards with a one-line value, scope or challenge statement | 9 | 0 | AWS, Microsoft, IBM, Adobe, Deloitte, Accenture, McKinsey, PwC, Cognizant | none | Accenture (overview page): opens every industry entry with a challenge line in that industry's terms | Industry directory |
| 6 | Coverage statement with a number | 2 | 0 | Oracle, Deloitte | none | Deloitte (overview page): states how many industries and sectors it covers, then names the sectors on each card | Industry directory (coverage count) |
| 7 | Sub-industry or segment navigation | 1 | 9 | Microsoft | AWS, Microsoft, Oracle, Deloitte, Accenture, McKinsey, PwC, Capgemini, Cognizant | AWS (industry page): a segments row with one page per segment | Segment links (industry page) |
| 8 | Second way in on the overview (capabilities, cross-industry processes, products by job) | 3 | 0 | Microsoft, SAP, Accenture | none | SAP (overview page): cross-industry process pages, each with a one-line outcome, beside the vertical list | Second route in (overview) |
| 9 | Why us, value pillars, differentiators | 3 | 3 | AWS, IBM, Oracle | AWS, Microsoft, SAP | AWS (industry page): four benefit statements in the body of the page, each a short paragraph | Why the company (overview) |
| 10 | Industry challenge statement or sector point of view | 0 | 7 | none | IBM, Adobe, Deloitte, Accenture, PwC, Capgemini, Cognizant | Deloitte (industry page): names the forces reshaping the industry before it says what it does | Answers per industry (overview), point of view (industry page) |
| 11 | Use cases or business priorities (tabs or cards, each with its answer) | 0 | 4 | none | IBM, SAP, Adobe, Accenture | IBM (industry page): each business priority pairs a problem paragraph with the one asset that answers it (webinar, guide or report) | Priorities and capabilities (industry page) |
| 12 | Solution and product mapping for the industry | 0 | 8 | none | AWS, Microsoft, IBM, Oracle, SAP, Deloitte, Capgemini, Cognizant | Oracle (industry page): line-of-business tabs, each listing sub-solutions in two or three plain sentences | Priorities and capabilities (industry page) |
| 13 | Full product index for the industry (A to Z) | 0 | 1 | none | Oracle | Oracle (industry page): a product directory grouped by solution and sector | Not used unless the portfolio has many products per industry |
| 14 | Partner ecosystem by industry (named partners, marketplace listings) | 1 | 4 | Accenture | AWS, Microsoft, SAP, Capgemini | Microsoft (industry page): named partners, each mapped to one job in the industry | Partners (industry page) |
| 15 | Customer logo strip (logos only) | 1 | 2 | Oracle | Oracle, SAP | Oracle (industry page): a logo carousel with no quote or number | Not used: logos alone are weak evidence |
| 16 | Case study cards (headline and teaser) | 3 | 10 | Microsoft, IBM, PwC | AWS, Microsoft, IBM, Adobe, Deloitte, Accenture, McKinsey, PwC, Capgemini, Cognizant | AWS (industry page): story cards with the outcome in each headline | Stories (overview), proof (industry page) |
| 17 | Customer outcome metrics shown as numbers | 2 | 7 | Microsoft, IBM | Microsoft, IBM, Adobe, Deloitte, PwC, Capgemini, Cognizant | Adobe (industry page): one bold metric under each of six customer logos, across the industry's segments | Proof beside the answer (overview), proof (industry page) |
| 18 | Named customer quote (name and title) | 0 | 2 | none | Microsoft, Adobe | Microsoft (industry page): each story card carries a quote, the speaker's title, one or two results and the products used | Stories (overview), proof (industry page) |
| 19 | Video (overview, customer or executive spotlight) | 2 | 4 | AWS, SAP | AWS, Microsoft, IBM, SAP | AWS (industry page): an executive customer spotlight video from a large customer in the industry | Optional: only when an industry video exists |
| 20 | Industry-firsts proof narrative | 1 | 0 | AWS | none | AWS (overview page): one paragraph of named firsts across industries, with no logo wall | Why the company (overview) |
| 21 | Vendor scale statistics (solutions, partners, years, regions) | 3 | 3 | AWS, SAP, Accenture | AWS, Oracle, Capgemini | AWS (overview page): two scale numbers (solutions and industry partners) in the first body section | Proof beside the answer (overview) |
| 22 | State-of-the-industry statistic strip | 0 | 2 | none | Oracle, Accenture | Accenture (industry page): four industry figures at the top of the page | Answers per industry (overview), point of view (industry page) |
| 23 | Third-party-sourced statistics (source named per figure) | 0 | 1 | none | Adobe | Adobe (industry page): three adoption figures, each with a named external source, one of them dated | Answers per industry (overview), point of view (industry page) |
| 24 | Analyst recognition and awards | 2 | 4 | IBM, Accenture | Oracle, Accenture, Capgemini, Cognizant | Accenture (industry page): recognition specific to the industry's sub-markets, each with firm, report, year, placement and field size | Recognition (overview), proof (industry page) |
| 25 | Resource library cards (typed: report, guide, e-book, webinar, blog) | 4 | 12 | AWS, Microsoft, IBM, PwC | all 12 | Capgemini (industry page): research cards labelled by kind (point of view, research, report) with a link to all insights for the industry | Research, outlooks and events |
| 26 | Year-labelled industry outlook or trends report | 3 | 6 | Microsoft, IBM, PwC | AWS, IBM, Deloitte, Accenture, PwC, Capgemini | Deloitte (industry page): a year-labelled outlook for every sector, plus annual predictions | Research, outlooks and events |
| 27 | Research with stated sample size or method | 0 | 1 | none | PwC | PwC (industry page): a survey card that states both of its sample sizes in the description | Research, outlooks and events (sample and method line) |
| 28 | Industry events (conference, forum, webinar, dated) | 3 | 3 | Microsoft, IBM, Oracle | IBM, SAP, Accenture | Accenture (industry page): an event card that gives the event's dates and venue | Research, outlooks and events |
| 29 | Named experts (leader cards with titles and contacts, bylined series, interviews) | 0 | 6 | none | Deloitte, Accenture, McKinsey, PwC, Capgemini, Cognizant | Deloitte (industry page): sector leaders with title, legal entity and direct contact routes | People |
| 30 | Visible publication dates on content cards | 0 | 2 | none | McKinsey, Capgemini | McKinsey (industry page): dates on its featured insight and case study cards | Research, outlooks and events (every card dated) |
| 31 | Named regulations, standards or certifications | 0 | 3 | none | Microsoft, Oracle, SAP | Microsoft (industry page): a full-width band on one named regulation | Trust and standards |
| 32 | Security, compliance and trust block | 1 | 3 | Microsoft | Microsoft, IBM, SAP | Microsoft (industry page): a security and compliance block on the industry page | Trust and standards |
| 33 | FAQ | 1 | 1 | Microsoft | SAP | SAP (industry page): seven questions, one or two sentence answers, links to trust evidence | FAQ |
| 34 | On-page AI assistant with suggested questions | 1 | 0 | Microsoft | none | Microsoft (overview page): an ask box with two suggested questions | Optional: suggested questions for an AI assistant |
| 35 | Interactive tool (calculator, explorer, lookup) | 0 | 1 | none | IBM | IBM (industry page): an ROI calculator offered as a card in the research row | Not used at launch unless a tool exists |
| 36 | Reference architectures or deployable templates | 0 | 0 | none | none | none in the starter set (open ground) | Not used: not seen on the starter set (add it only when technical buyers expect architectures) |
| 37 | Named methodology or playbook | 1 | 1 | Oracle | Deloitte | Oracle (overview page): industry playbooks framed as planning standards and tools | Not used unless the client has a named method |
| 38 | Innovation labs or studios | 2 | 0 | IBM, Oracle | none | Oracle (overview page): physical industry lab sites where customers test solutions | Not used unless the client runs labs |
| 39 | Proprietary benchmarks and data products | 0 | 1 | none | McKinsey | McKinsey (industry page): named benchmarking and data products with plain one-line definitions | Not used unless the client sells benchmark or data products |
| 40 | Product road map by industry | 0 | 1 | none | SAP | SAP (industry page): public product road maps, one per segment, in the get-started block | Not used unless a public road map exists |
| 41 | Free trials and offers | 0 | 0 | none | none | none in the starter set (open ground) | Not used: not seen on the starter set (the offer belongs in the closing band) |
| 42 | Newsletter subscription (industry intelligence) | 2 | 2 | IBM, PwC | Deloitte, PwC | PwC (overview page): an industry-intelligence subscription framed around what is coming for the reader's industry | Closing band (newsletter option) |
| 43 | Contact and next steps (closing button, multi-path next steps, phone or RFP shortcuts) | 7 | 10 | AWS, Microsoft, IBM, Adobe, McKinsey, Capgemini, Cognizant | AWS, Microsoft, IBM, SAP, Adobe, Deloitte, McKinsey, PwC, Capgemini, Cognizant | Microsoft (industry page): next steps that route to responsible-use principles, a trust portal and documentation, not only to sales | Closing band |
| 44 | Cross-links to other site sections (services, alliances, governance, careers) | 4 | 1 | IBM, Deloitte, Accenture, McKinsey | Accenture | McKinsey (overview page): links to the firm's history and its client service policies | Closing band (related links) |
| 45 | Page feedback widget | 1 | 1 | SAP | SAP | SAP (industry page): a page feedback prompt at the foot of the page | Not used: a site-wide feature, not a page section |

An assistant launcher (a site widget, not counted as a section) was also seen on 3 overview pages and 3 industry
pages.

## Not seen on any of the 24 pages
Podcasts, glossaries, maturity or readiness self-assessments (a calculator and a gated readiness guide come
closest), comparison tables, pricing by industry, reference architectures (type 36) and free trials or offers
(type 41). Treat
these as open ground: a block no page in the set has can set the client apart when the client's proof supports it.
Add it as a new type id and count it before you claim it.

## Less common sections worth considering
Seen on few pages, high value for buyers and for AI answers:
1. Year-labelled outlooks per sector (type 26): current thinking; answer engines prefer dated research for trend
   questions.
2. Research that states its sample size (27): the reader can judge the evidence; an answer can cite the figure with
   its sample.
3. Figures with a named third-party source and date (23): the most citable proof format in the set.
4. A state-of-the-industry strip (22): a few industry figures at the top of the page, each with a source and a
   date.
5. Analyst recognition specific to the industry (24): firm, report, year, placement and field size in one line.
6. Named industry leaders with titles and a contact route (29): authorship and expertise tied to the topic.
7. Industry events with dates and venue (28), as visible text.
8. Named regulations and certifications (31): a yes or no answer to "do you support X".
9. An industry FAQ (33): the standard objections answered without a call, phrased as buyers ask them.
10. Sub-industry navigation with its own pages (7): a dedicated address per segment to cite.
11. Partners mapped to industry jobs (14), not a logo wall.
12. A story card that carries a result, a named quote and the product used (18).
13. An interactive calculator (35): a linkable tool answer engines can recommend.
14. An industry challenge statement or sector point of view (10): the reader's problem named in their terms.

Seen once and worth a thought: public product road maps per segment (40), a named method or playbook (37), physical
labs (38), proprietary benchmark products (39), an industry-firsts
paragraph (20), and a research-first overview page where every card shows its format and read time.

## Quality warnings (things not to copy)
- Test or placeholder copy live on a crawlable page (an event block, image alt text). Check every block before
  launch.
- Figures with no source, or a forecast whose horizon has already passed.
- Counts that disagree between the meta description and the body (number of industries, years in business).
- Proof lines with errors: check firm and report names, years and placements against the source.
- A template date stamp printed near the H1 that reads like a content date but is not one.
- An obvious overview address that returns a 404 or redirects to the homepage while the list lives elsewhere.
- Hero content in an embed or script-only widget with no crawlable text.
- Event facts (dates, venue) that show only on hover.
- FAQPage markup with no visible FAQ, and visible FAQs with no markup.
- Most pages carried no structured data beyond BreadcrumbList or WebPage, and many images had no alt text.
