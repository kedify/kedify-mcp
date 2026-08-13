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
├── agents/
│   └── openai.yaml
└── references/
    └── autoscaling-checks.md
```

Rules:

- `SKILL.md` must be at the archive root.
- Only files from that skill directory are included.
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
- `.codex-plugin/plugin.json` version: `0.1.0`
- release asset: `kedify-mcp-autoscaling-debug-v0.1.0.zip`

## Release steps

1. Update skill or plugin-packaging source files in this repo.
2. If needed, deploy compatible MCP backend changes from `dashboard-api-service` first.
3. Bump `.codex-plugin/plugin.json` `version`.
4. Merge to `main`.
5. Tag the release:

```bash
git tag v0.1.0
git push origin v0.1.0
```

6. GitHub Actions will:
   - validate plugin manifests
   - validate each skill
   - build one zip per skill into `dist/`
   - verify archive structure against the source skill directory
   - attach the zip files and `SHA256SUMS.txt` to the GitHub Release

## Local release checks

Run the same checks locally before tagging:

```bash
python -m pip install --upgrade pip pyyaml
python scripts/validate_plugin.py
python scripts/validate_skills.py
python scripts/build_skill_archives.py --out dist
python scripts/verify_archives.py dist
```

## ChatGPT upload

For manual ChatGPT skill upload, use the per-skill zip from the GitHub Release.

The repo also supports OpenAI's MCP skill import flow, but that is not the primary release path here. Uploadable skill zips are the default because they are predictable, easy to review, and do not depend on rescanning MCP resources during release handling.

## Repository boundary

Keep the split clear:

- `kedify-mcp`: plugin packaging, bundled skills, release zips
- `dashboard-api-service`: MCP server runtime, Auth0 integration, tool behavior, backend deployment

Do not add backend server code to this repository.
