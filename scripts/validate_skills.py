#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any

from common import discover_skill_dirs, load_yaml, parse_skill_frontmatter


def main() -> None:
    errors: list[str] = []
    skill_dirs = discover_skill_dirs()
    if not skill_dirs:
        errors.append("no skill directories were found under skills/")

    for skill_dir in skill_dirs:
        validate_skill_dir(skill_dir, errors)

    if errors:
        print("Skill validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print(f"Skill validation passed for {len(skill_dirs)} skill(s)")


def validate_skill_dir(skill_dir: Path, errors: list[str]) -> None:
    skill_md_path = skill_dir / "SKILL.md"
    try:
        frontmatter = parse_skill_frontmatter(skill_md_path)
    except ValueError as exc:
        errors.append(str(exc))
        return

    name = frontmatter.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append(f"{skill_md_path} frontmatter field `name` must be non-empty")
    elif name != skill_dir.name:
        errors.append(
            f"{skill_md_path} frontmatter name `{name}` must match directory `{skill_dir.name}`"
        )

    description = frontmatter.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append(f"{skill_md_path} frontmatter field `description` must be non-empty")

    agent_yaml_path = skill_dir / "agents" / "openai.yaml"
    if agent_yaml_path.is_file():
        validate_agent_yaml(skill_dir, agent_yaml_path, errors)


def validate_agent_yaml(skill_dir: Path, agent_yaml_path: Path, errors: list[str]) -> None:
    payload = load_yaml(agent_yaml_path)
    if not isinstance(payload, dict):
        errors.append(f"{agent_yaml_path} must contain a YAML object")
        return

    interface = payload.get("interface")
    if not isinstance(interface, dict):
        errors.append(f"{agent_yaml_path} field `interface` must be an object")
        return

    for field in ("display_name", "short_description"):
        value = interface.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{agent_yaml_path} field `interface.{field}` must be non-empty")

    default_prompt = interface.get("default_prompt")
    if default_prompt is not None and (not isinstance(default_prompt, str) or not default_prompt.strip()):
        errors.append(f"{agent_yaml_path} field `interface.default_prompt` must be non-empty")

    dependencies = payload.get("dependencies")
    if dependencies is None:
        return
    if not isinstance(dependencies, dict):
        errors.append(f"{agent_yaml_path} field `dependencies` must be an object")
        return

    tools = dependencies.get("tools")
    if tools is None:
        return
    if not isinstance(tools, list):
        errors.append(f"{agent_yaml_path} field `dependencies.tools` must be an array")
        return

    for index, tool in enumerate(tools):
        validate_dependency_tool(skill_dir, agent_yaml_path, tool, index, errors)


def validate_dependency_tool(
    skill_dir: Path,
    agent_yaml_path: Path,
    tool: Any,
    index: int,
    errors: list[str],
) -> None:
    label = f"{agent_yaml_path} dependency #{index}"
    if not isinstance(tool, dict):
        errors.append(f"{label} must be an object")
        return

    tool_type = tool.get("type")
    if not isinstance(tool_type, str) or not tool_type.strip():
        errors.append(f"{label} field `type` must be non-empty")
        return

    value = tool.get("value")
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} field `value` must be non-empty")

    if tool_type == "mcp":
        url = tool.get("url")
        if not isinstance(url, str) or not url.strip():
            errors.append(f"{label} field `url` must be non-empty for MCP dependencies")


if __name__ == "__main__":
    main()
