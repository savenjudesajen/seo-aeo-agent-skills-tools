# Retiring prompts without losing their history

Prompts carry accumulated visibility data, and analytics are usually reported per container (a project or
workspace, depending on the platform). Do not delete a retired prompt until its history is safe.

## Order

1. **Owner sign-off on the audit sheet first.** Nothing moves before it.
2. **Check whether an older container already holds the prompts** (an earlier project or workspace version). If it
   does and its history covers the tracked period, the prompts can be removed from the current container.
3. **If not, move them to an archive container** named for what it is (e.g. "<Brand> archive - pre <month year>
   positioning"). Confirm on a pilot of a few prompts that the history moved with them; if the platform cannot move
   history, keep them live in the archive container instead of deleting.
4. **Then remove them from the current container**, leaving it with the final list only.
5. **Rewrites are new prompts.** Load the rewritten text as a new prompt and retire the old one through steps 2 to 4;
   do not edit a prompt's text in place where the platform keeps history per prompt, because the trend line would
   join two different questions.
6. **Log the change date** in the deliverable and the report notes: the visibility denominator changes that day, and a
   week-on-week comparison across it is not like for like.

## Platform notes

Mechanics come from the platform's own documentation. Check before step 3 whether a delete (in the UI or through the
API) is a hard delete with no restore. On some platforms it is, and then step 3 is not optional.
