# What you do, and the few things that go back to the user

The point of this skill is that a content refresh reaches production without the user driving a
terminal. Treat any hand-back as a defect to be designed out, except for the genuinely credential-gated
steps below.

## Yours

Repo recon, reading the renderer, converting content, writing and running the apply script, all four
gates, the PR body, checking deploy state, verifying the live pages, updating the tracker, and
diagnosing anything that failed.

## Legitimately theirs

**Anything requiring their credentials.** You don't handle tokens, passwords or auth flows. In practice
that is:

- the initial `git clone` of a private repo;
- `git push`;
- account-level changes on the deploy platform (linking a GitHub account, inviting a user to a team).

When you hand one of these back:

- **Give it as one single line, not a multi-line block.** PowerShell and bash both prompt for
  continuation on every extra line, so a four-line block is four interactions and an easy place to drop
  a `cd`. Chain with `;`:
  `cd <path>; git checkout main; git pull; git merge --no-ff <branch> -m "..."; git push`
- Say in one line why it needs them specifically.
- State what you will do the moment it lands, and then do it without asking again.

Budget the hand-backs like a scarce resource. Two per publish is the ceiling: one to push, one to merge.
If you are on your third, something you did caused it.

## Reducing the hand-backs

- Ask for the clone once, at the start, and keep the working copy for the rest of the engagement. A
  second refresh into the same repo then needs only a pull and a push.
- Prefer a persistent shared working folder over re-cloning.
- Batch the credentialed steps: one paste that clones, or one paste that commits and pushes, rather
  than a conversation per command.

## Things that look like a shortcut but aren't yours to take

- Creating a deploy hook to dodge an author check the client enabled on purpose.
- Inviting an account to the client's paid team to unblock yourself.
- Weakening branch protection or review requirements.
- Committing under someone else's identity to satisfy a deploy check.

Each of these is a change to the client's security posture. Surface the option, explain the tradeoff,
and let them decide.
