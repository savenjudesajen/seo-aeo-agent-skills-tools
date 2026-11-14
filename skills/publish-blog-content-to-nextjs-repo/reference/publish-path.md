# Branch, commit, PR, merge, deploy

Contents: 0. Establish the deploy-linked identity first · 1. Prepare the working copy · 2. Apply and verify · 3. Commit as the deploy-linked identity · 4. PR body · 5. Merge from the CLI · 6. Confirm the deploy; don't assume it · 7. Verify live

## 0. Establish the deploy-linked identity first

Do this before you commit anything. It is the cheapest step in the sequence, and skipping it is what
turns a clean ship into a two-cycle one.

Deploy platforms can gate builds on the **git author of the commit**, not on who pushed. You need to
know, up front, which identity the platform accepts.

How to find it without asking anyone:

1. Open the project's deployment history.
2. Find the production deployments that reached `Ready`.
3. Look up those commits on the host and note the **author**. That account is linked and accepted.

A successful **preview** build is equally good evidence, because the same author gate applies to
previews. If your content branch's preview passed, the identity that authored that commit can safely own
the merge commit too.

Then check the working copy agrees:

```
git config user.name; git config user.email
```

On agency or contractor work there are often two identities in play: the one with **repo access** and
the one with a **deploy-platform account**. They are frequently not the same account, and repo access
tells you nothing about deploy eligibility. Write the accepted one into config as
`deploy_linked_git_identity`.

## 1. Prepare the working copy

If the clone is fresh and came from Windows, normalize line endings first:

```
git config core.autocrlf false
git rm --cached -r . -q
git reset --hard
git checkout -b <branch>
```

Skipping this means the first commit carries every text file in the repo.

## 2. Apply and verify

Before applying, save a copy of each content file you will touch (or use `git show HEAD:<path>`), so
`verify_publish.py untouched` can compare before and after.

Run `data/apply_content.py`, then all four gates. The typecheck matters even though you only changed
strings: it proves the structured-data field satisfies the post interface and that nothing broke the
array's shape.

When the full project can't build for want of environment variables, typecheck the data layer alone. It
is usually self-contained (no framework imports), which makes a standalone strict `tsc` run a complete
check of what you changed rather than a partial one. Say which of the two you ran.

## 3. Commit as the deploy-linked identity

Check it before committing:

```
git config user.name; git config user.email
```

If this does not match `deploy_linked_git_identity`, the deploy will be blocked.

Stage explicit paths rather than `-A`, so nothing incidental rides along.

## 4. PR body

The body is where you disclose what a reviewer can't see in the diff:

- which posts, which files, which titles changed and why;
- **the format the content had to be converted to, and why**;
- **every lossy conversion**: dropped embeds, downgraded blocks;
- the structured-data convention you followed and where it came from;
- what you verified, with numbers (gate 1 counts, typecheck mode);
- what you deliberately left out, as follow-ups.

A reviewer who learns about a dropped video from the live site rather than the PR body won't trust the
next PR.

## 5. Merge from the CLI

```
git checkout <default_branch>
git pull
git merge --no-ff <branch>
git push
```

**Not** the web Merge button. The trap is subtle: your content commit can carry the correct,
deploy-linked author and the deploy still blocks, because the web button creates a **separate merge
commit** authored by whoever is signed into the browser. On agency or contractor work that is usually
the repo-access account, not the deploy-linked one. The diff is perfect; the deploy never runs.

If the client requires review before merge, hand off at the PR and say so.

## 6. Confirm the deploy; don't assume it

A merged PR is not a deploy. Check the deployment reached `Ready`.

States worth recognizing:

- `Blocked`: almost always the git-author link. It can't be redeployed; land a fresh commit from the
  linked identity (an empty commit is enough).
- `Queued`: a concurrency limit; wait.
- `Error`: read the build log. If it fails on something you did not touch, say so rather than "fixing"
  unrelated code.

## 7. Verify live

Fetch every changed URL. Assert 200, the new title, the expected block counts, structured data present,
zero Markdown leaks, and compare the counts with gate 1's prediction. Only then report done.
