# kedify-mcp

This repository contains Kedify plugin packaging only. It owns the Codex/OpenAI plugin manifests, bundled skills, and packaging docs for the hosted Kedify MCP server.

It does not contain the MCP backend implementation. The actual server, tool catalog, Auth0 integration, and runtime deployment live in the separate `dashboard-api-service` repository.

## Repository scope

- `.codex-plugin/plugin.json`: plugin manifest and UI metadata
- `.mcp.json`: hosted Kedify MCP server declaration
- `.app.json`: compatibility manifest for registered MCP server mappings
- `skills/`: plugin-bundled skills that guide use of the hosted MCP tools

## Backend separation

Keep this repository packaging-only.

- Backend repo: `dashboard-api-service`
- Hosted production MCP URL: `https://mcp.kedify.io/mcp`
- Hosted production OAuth resource/audience: `https://mcp.kedify.io`
- Hosted development MCP URL: `https://mcp.dev.kedify.io/mcp`
- Hosted development OAuth resource/audience: `https://mcp.dev.kedify.io`

The plugin connects to the hosted MCP server over streamable HTTP through `.mcp.json`. No MCP server code should be added to this repository.

## Packaging choice

This scaffold keeps the actual MCP endpoint in `.mcp.json`, because OpenAI's plugin packaging docs describe `.mcp.json` as MCP server configuration and `.app.json` as a compatibility mapping file for registered MCP server connections.

`.app.json` is intentionally minimal. It is included so this repo owns the full plugin-packaging surface, but it does not declare a connector-specific registered mapping yet. If Kedify later gets a dedicated ChatGPT/Codex registered MCP connection, populate `.app.json` with that mapping instead of moving MCP transport settings out of `.mcp.json`.

## Local testing

By default, `.mcp.json` points at production:

```json
{
  "mcpServers": {
    "kedify": {
      "type": "http",
      "url": "https://mcp.kedify.io/mcp",
      "oauth_resource": "https://mcp.kedify.io"
    }
  }
}
```

For development testing, switch those two values to:

- `https://mcp.dev.kedify.io/mcp`
- `https://mcp.dev.kedify.io`

Validate the plugin and bundled skills locally with:

```bash
python3 scripts/validate_plugin.py
python3 scripts/validate_skills.py
```

If you want Codex to load this repo as a local plugin, the simplest path is to expose this repo at `~/plugins/kedify-mcp` and use a local marketplace entry that points to `./plugins/kedify-mcp`.

Example:

```bash
mkdir -p ~/plugins
ln -sfn /home/jkarasek/go/src/github.com/kedify/kedify-mcp ~/plugins/kedify-mcp
```

After the marketplace entry exists, use the normal local update flow:

1. Refresh the plugin cachebuster:

```bash
python3 /home/jkarasek/.codex/skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py \
  /home/jkarasek/go/src/github.com/kedify/kedify-mcp
```

2. Reinstall the plugin from the configured local marketplace:

```bash
codex plugin add kedify-mcp@personal
```

3. Start a new Codex thread so updated skills and MCP metadata are picked up cleanly.

## Bundled skill

The initial bundled skill is `skills/kedify-mcp-autoscaling-debug`. It is packaging-local guidance for using the hosted MCP capability `clusters.debug_autoscaling_checks` and related read-only autoscaling debugging tools. Its `agents/openai.yaml` declares the hosted Kedify MCP dependency so the skill remains aligned with OpenAI's current plugin skill packaging guidance.

## Releasing

Release artifacts are optimized for ChatGPT skill upload.

- one GitHub Release tag per repo version
- one zip artifact per skill
- no separate whole-plugin zip release artifact

See [RELEASING.md](/home/jkarasek/go/src/github.com/kedify/kedify-mcp/RELEASING.md:1) for the exact artifact layout, versioning model, and GitHub Actions release flow.
