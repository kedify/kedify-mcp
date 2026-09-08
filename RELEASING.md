# Releasing `kedify-mcp`

This repository publishes ChatGPT-upload-friendly skill archives.

## Source of truth

This repo is the source of truth for:

- `skills/`
- `.codex-plugin/plugin.json`
- `.mcp.json`
- `.app.json`

This repo does not contain the Kedify MCP backend implementation. The backend lives in `dashboard-api-service`.

## Release model

Release one zip per skill.

Why this is the default:

- ChatGPT skill upload works cleanly with a packaged skill archive.
- A skill zip can include `SKILL.md`, `agents/openai.yaml`, and supporting files such as `references/`.
- Teammates can quickly identify the right release asset to upload.

We do not publish a separate whole-plugin zip as a custom release artifact. GitHub's tag/source archives already preserve the full repo snapshot when someone needs the full packaging source.

## Artifact layout

Each skill archive contains exactly one skill root with no extra wrapper directory.

Example:

```text
kedify-mcp-autoscaling-debug-v0.1.0.zip
├── SKILL.md
├── LICENSE
├── agents/
│   └── openai.yaml
└── references/
    └── autoscaling-checks.md
```

Rules:

- `SKILL.md` must be at the archive root.
- Only files from that skill directory are included.
- Each skill directory includes its applicable `LICENSE` so every archive
  carries the full license text. The current skills use the same Apache 2.0
  text as the repository root.
- Repo-level plugin files such as `.codex-plugin/plugin.json`, `.mcp.json`, `.app.json`, and `README.md` are never included in skill zips.

## Naming

Skill archives use repo-wide versioning:

- `<skill-name>-v<repo-version>.zip`

Examples:

- `kedify-mcp-autoscaling-debug-v0.1.0.zip`

The release job also attaches:

- `SHA256SUMS.txt`

## Versioning

Use repo-wide versioning only.

Reasons:

- plugin packaging and bundled skills ship together from one repository
- there is currently one bundled skill
- per-skill versioning would add coordination cost without helping the ChatGPT upload flow

Versioning convention:

- Git tag: `v0.1.0`
- release-stamped `.codex-plugin/plugin.json` version: `0.1.0`
- release asset: `kedify-mcp-autoscaling-debug-v0.1.0.zip`

## Release steps

Preferred local release command:

```bash
python scripts/cut_release.py --version 0.1.0 --push
```

What it does:

- requires a clean git worktree
- stamps `.codex-plugin/plugin.json` to `0.1.0`
- validates plugin and skills
- builds and verifies the skill archives locally
- commits the version bump with `release: v0.1.0`
- creates annotated tag `v0.1.0`
- pushes the current branch and tag when `--push` is passed

Manual step-by-step equivalent:

1. Update skill or plugin-packaging source files in this repo.
2. If needed, deploy compatible MCP backend changes from `dashboard-api-service` first.
3. Merge to `main`.
4. Run:

```bash
python scripts/cut_release.py --version 0.1.0
```

5. If you did not use `--push`, push the branch and tag:

```bash
git push origin HEAD
git push origin v0.1.0
```

6. GitHub Actions will:
   - stamp `.codex-plugin/plugin.json` to the tag version inside the CI workspace
   - validate plugin manifests
   - validate each skill
   - build one zip per skill into `dist/`
   - verify archive structure against the source skill directory
   - attach the zip files and `SHA256SUMS.txt` to the GitHub Release

## Local release checks

Run the same checks locally before tagging:

```bash
python -m pip install --upgrade pip pyyaml
python scripts/set_plugin_version.py --version 0.1.0
python scripts/validate_plugin.py --expected-version 0.1.0
python scripts/validate_skills.py
python scripts/build_skill_archives.py --version 0.1.0 --out dist
python scripts/verify_archives.py dist
```

You can also preview the release cutter without changing git state:

```bash
python scripts/cut_release.py --version 0.1.0 --dry-run
```

## ChatGPT upload

For manual ChatGPT skill upload, use the per-skill zip from the GitHub Release.

The repo also supports OpenAI's MCP skill import flow, but that is not the primary release path here. Uploadable skill zips are the default because they are predictable, easy to review, and do not depend on rescanning MCP resources during release handling.

## Repository boundary

Keep the split clear:

- `kedify-mcp`: plugin packaging, bundled skills, release zips
- `dashboard-api-service`: MCP server runtime, Auth0 integration, tool behavior, backend deployment

Do not add backend server code to this repository.
