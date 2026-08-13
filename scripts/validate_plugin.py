#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from common import PLUGIN_MANIFEST_PATH, PLUGIN_ROOT, ensure_semver, load_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate kedify-mcp plugin packaging files.")
    parser.add_argument(
        "--expected-version",
        help="Expected plugin manifest version, typically derived from a release tag.",
    )
    args = parser.parse_args()

    errors: list[str] = []
    validate_plugin_manifest(errors, args.expected_version)
    validate_mcp_manifest(errors)
    validate_app_manifest(errors)

    if errors:
        print("Plugin validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("Plugin validation passed")


def validate_plugin_manifest(errors: list[str], expected_version: str | None) -> None:
    if not PLUGIN_MANIFEST_PATH.is_file():
        errors.append("missing .codex-plugin/plugin.json")
        return

    payload = load_json(PLUGIN_MANIFEST_PATH)
    if not isinstance(payload, dict):
        errors.append(".codex-plugin/plugin.json must contain a JSON object")
        return

    required_strings = (
        "name",
        "version",
        "description",
    )
    for field in required_strings:
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"plugin.json field `{field}` must be a non-empty string")

    version = payload.get("version")
    if isinstance(version, str):
        ensure_semver(version, "plugin.json field `version`", errors)
        if expected_version is not None and version != expected_version:
            errors.append(
                f"plugin.json version `{version}` does not match release tag `{expected_version}`"
            )

    author = payload.get("author")
    if not isinstance(author, dict):
        errors.append("plugin.json field `author` must be an object")
    else:
        name = author.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append("plugin.json field `author.name` must be a non-empty string")

    skills = payload.get("skills")
    if skills != "./skills/":
        errors.append("plugin.json field `skills` must be `./skills/`")
    elif not (PLUGIN_ROOT / "skills").is_dir():
        errors.append("skills directory is missing")

    apps = payload.get("apps")
    if apps is not None and apps != "./.app.json":
        errors.append("plugin.json field `apps` must be `./.app.json` when present")

    mcp_servers = payload.get("mcpServers")
    if mcp_servers is not None and mcp_servers != "./.mcp.json":
        errors.append("plugin.json field `mcpServers` must be `./.mcp.json` when present")

    interface = payload.get("interface")
    if not isinstance(interface, dict):
        errors.append("plugin.json field `interface` must be an object")
        return

    for field in (
        "displayName",
        "shortDescription",
        "longDescription",
        "developerName",
        "category",
    ):
        value = interface.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"plugin.json field `interface.{field}` must be a non-empty string")

    capabilities = interface.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities:
        errors.append("plugin.json field `interface.capabilities` must be a non-empty array")
    elif not all(isinstance(item, str) and item.strip() for item in capabilities):
        errors.append("plugin.json field `interface.capabilities` must contain strings")

    default_prompt = interface.get("defaultPrompt")
    if not isinstance(default_prompt, list) or not default_prompt:
        errors.append("plugin.json field `interface.defaultPrompt` must be a non-empty array")
    elif not all(isinstance(item, str) and item.strip() for item in default_prompt):
        errors.append("plugin.json field `interface.defaultPrompt` must contain strings")


def validate_mcp_manifest(errors: list[str]) -> None:
    path = PLUGIN_ROOT / ".mcp.json"
    if not path.is_file():
        errors.append("missing .mcp.json")
        return

    payload = load_json(path)
    if not isinstance(payload, dict):
        errors.append(".mcp.json must contain a JSON object")
        return

    server_map = extract_server_map(payload)
    if server_map is None:
        errors.append(".mcp.json must contain an MCP server map")
        return
    if not server_map:
        errors.append(".mcp.json must define at least one MCP server")
        return

    for server_name, config in server_map.items():
        if not isinstance(server_name, str) or not server_name.strip():
            errors.append(".mcp.json server names must be non-empty strings")
            continue
        if not isinstance(config, dict):
            errors.append(f".mcp.json server `{server_name}` must be an object")
            continue
        validate_server_config(server_name, config, errors)


def extract_server_map(payload: dict[str, Any]) -> dict[str, Any] | None:
    for key in ("mcpServers", "mcp_servers"):
        value = payload.get(key)
        if value is not None:
            return value if isinstance(value, dict) else None
    return payload


def validate_server_config(server_name: str, config: dict[str, Any], errors: list[str]) -> None:
    has_command = isinstance(config.get("command"), str) and config["command"].strip()
    has_url = isinstance(config.get("url"), str) and config["url"].strip()
    if not has_command and not has_url:
        errors.append(f".mcp.json server `{server_name}` must define either `url` or `command`")

    server_type = config.get("type")
    if has_url and server_type is not None and server_type != "http":
        errors.append(f".mcp.json server `{server_name}` uses `url` and should set `type` to `http`")
    if has_url and not isinstance(config.get("url"), str):
        errors.append(f".mcp.json server `{server_name}` field `url` must be a string")
    if "args" in config and not isinstance(config["args"], list):
        errors.append(f".mcp.json server `{server_name}` field `args` must be an array")


def validate_app_manifest(errors: list[str]) -> None:
    path = PLUGIN_ROOT / ".app.json"
    if not path.is_file():
        errors.append("missing .app.json")
        return

    payload = load_json(path)
    if not isinstance(payload, dict):
        errors.append(".app.json must contain a JSON object")
        return

    apps = payload.get("apps")
    if not isinstance(apps, dict):
        errors.append(".app.json field `apps` must be an object")
        return

    for app_name, config in apps.items():
        if not isinstance(app_name, str) or not app_name.strip():
            errors.append(".app.json app names must be non-empty strings")
            continue
        if not isinstance(config, dict):
            errors.append(f".app.json app `{app_name}` must be an object")
            continue
        if "id" not in config:
            errors.append(f".app.json app `{app_name}` must define `id`")
            continue
        if not isinstance(config["id"], str) or not config["id"].strip():
            errors.append(f".app.json app `{app_name}` field `id` must be a non-empty string")


if __name__ == "__main__":
    main()
