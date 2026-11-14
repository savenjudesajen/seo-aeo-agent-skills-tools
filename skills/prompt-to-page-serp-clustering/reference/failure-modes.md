# Failure modes and guards

1. **Agent completion confabulation.** Agents given large batches (30+ full SERP responses) run out of
   context and report unfetched rows as "skipped". Guard: small batches (12); instruct "report
   unprocessed rows as REMAINING, never as skipped"; **never trust agent counts, verify on disk.**

2. **Interrupted turns still execute.** A turn cut off mid-flight may already have launched agents whose
   checkpoints appear later with no trace in context. Guard: **always inventory disk before
   relaunching**. Skip-if-exists makes a double launch harmless; that is the design working.

3. **The authenticity check trio** for disk data of uncertain origin: (a) the API's own call meter (a
   usage delta proves real calls happened; read it before AND after big runs), (b) file forensics
   (mtime windows, schema fingerprint, presence of fields like `elapsed_s`), (c) URL-diversity stats
   (real SERP sets have a high share of singleton domains and many distinct domains; fabricated data
   looks uniform). Run all three before trusting orphan checkpoints.

4. **Tool responses flood the caller's context.** A full SERP response is roughly 10 KB, and trend
   series (52 weekly points per keyword) are worse. Fan out to disposable agent contexts and return only
   counts and verdicts. The main context runs the engine and the judgment, **never the transport**.

5. **The authored-intent prior (signal B) is not evidence.** See `signal-provenance.md`. Spot-check every
   low-support assignment and flag REVIEW rather than force.

6. **Confidence is inherited from the CLUSTER, not the row.** Expose the row's own evidence.

7. **NET-NEW is a negative test.** Absence of overlap is not demand. Always run the escalation
   adjudication (`pipeline.md` step 6).

8. **The seed keyword is not the prompt.** Head-term inflation credits prompts with a whole category's
   demand; a noticeable share of new-page verdicts lean on a seed doing hundreds or thousands a month.
   Guard: seed-ownership check plus page-inventory reasoning.

9. **Token or slug matching cannot decide "does this page already exist?"** Use a reasoning pass over
   the real inventory.

10. **The grain guard cannot see `X vs Y`.** Enforce competitor-vs-competitor by reviewer rule.

11. **Positional write-back of a parallel batch.** One error in a batch shifts every later result onto
    the wrong id. Key results to the requested id and reconcile counts before persisting.

12. **A crashed step leaves the previous artifact on disk.** The next step consumes it and the gates pass
    on stale data. Check the exit code of every step.

13. **Modelled "prompt volume" fields can come back zero or flat for every prompt.** If a volume field
    returns the same bucket for the whole corpus, including prompts with clear demand, treat it as
    unavailable and fall back to seed-keyword volume plus trend.

14. **Mention tools are not citation tools, and their fields need checking.** A visibility tool may
    report sentiment for an engine where the brand was not mentioned, or a "position" that is a
    character offset rather than a rank. Read the field definitions before reporting them.

15. **Bulk loads into a tracking tool can hit an undocumented project-wide cap** and fail atomically
    (nothing loaded). Check and raise the cap before a bulk load.

16. **Workspaces reset.** A sandbox can be wiped between sessions and take a whole fetch with it. The
    durable layer is the scripts, this skill and stable ids; present final artifacts to the user's
    machine before the session ends.

---

# Run sizing (rules of thumb)

- **Agent context ceiling:** about a dozen full SERP responses per agent before it stops and
  confabulates completion. Batch size 12 is the safe number; a lean URL-only provider roughly halves
  transport cost, so lean batches can go to about 24 per agent.
- **Concurrency:** up to 6 concurrent agents is a sensible default; watch for rate limits and back off
  if the provider throttles. With several agents sharing one shell, have them check file existence
  with file-read or glob tools rather than shell listings.
- **Latency:** a full SERP call takes several seconds to tens of seconds; requeries are slower; expect an
  occasional client timeout that a retry fixes. Latency varies with time of day.
- **Trend calls:** batch a few keywords per call and never pull the series into the main context.
- **Re-runs are cheap** once overrides exist: a full re-cluster, re-assign, gates and workbook take
  minutes because only the gate delta needs reasoning.
