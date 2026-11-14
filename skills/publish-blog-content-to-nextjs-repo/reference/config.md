# Per-client config

Establish these before Phase 1. Nothing in this skill is hardcoded to a client. Keep the resolved
values for later runs so they skip the discovery.

```json
{
  "repo": "https://github.com/<org>/<repo>.git",
  "default_branch": "main",
  "content_layout": "ts_object_literals",
  "content_files": ["src/content/<file>.ts"],
  "renderer_path": "src/app/blog/[slug]/page.tsx",
  "interface_path": "src/content/<types file>.ts",
  "url_pattern": "https://<domain>/blog/<slug>",
  "deploy_platform": "vercel",
  "deploy_linked_git_identity": "Name <deploy-user@example.com>",
  "local_clone_path": "<path to the user's working copy>"
}
```

The paths above are placeholders; read the real ones off the repo.

## The fields that matter

**`content_layout`**: three shapes show up in practice.

- `ts_object_literals`: post bodies are template literals inside a typed array. Editing means a careful
  in-place string replace. This is the hardest case and the one `data/apply_content.py` is written for.
- `mdx_files`: one file per post. Easiest: write the file (keeping its frontmatter conventions), done.
- `headless_cms`: the repo is irrelevant; the content lives behind an API. Stop and ask which CMS before
  proceeding.

**`deploy_linked_git_identity`**: the single most important field. It is the git author whose GitHub
account has a linked account on the deploy platform. Commits and merges must carry this identity or the
deploy is blocked. Find it by looking at which past deployments reached `Ready` and who authored those
commits.

**`renderer_path`**: the file that turns stored content into HTML. Read it in full. Never assume it uses
a Markdown library.

**`interface_path`**: the type the posts satisfy. The typecheck gate proves your structured-data field
and metadata fit it.

## Recording per-client facts

After a successful run, record the slug-to-file map and the deploy identity. On a repo with several
content files, knowing which file holds which slug saves a full re-scan every time. Record the
renderer's grammar too (the `SUPPORTED` / `LEAKS` tables you set in `verify_publish.py`), and whether
gate 1's prediction matched the live counts.
