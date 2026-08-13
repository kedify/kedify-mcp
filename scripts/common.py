from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
SKILLS_ROOT = PLUGIN_ROOT / "skills"
PLUGIN_MANIFEST_PATH = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)"
    r"(?:-(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)(?:\."
    r"(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_yaml(path: Path) -> Any:
    import yaml

    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_skill_frontmatter(skill_md_path: Path) -> dict[str, Any]:
    import yaml

    contents = read_text(skill_md_path)
    if not contents.startswith("---\n"):
        raise ValueError(f"{skill_md_path} must start with YAML frontmatter")
    end = contents.find("\n---", 4)
    if end == -1:
        raise ValueError(f"{skill_md_path} frontmatter is not closed")
    payload = yaml.safe_load(contents[4:end])
    if not isinstance(payload, dict):
        raise ValueError(f"{skill_md_path} frontmatter must be a YAML object")
    return payload


def discover_skill_dirs() -> list[Path]:
    if not SKILLS_ROOT.is_dir():
        return []
    return sorted(
        path
        for path in SKILLS_ROOT.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )


def normalize_relpath(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def ensure_semver(version: str, label: str, errors: list[str]) -> None:
    if SEMVER_RE.fullmatch(version) is None:
        errors.append(f"{label} must be valid semver")


def plugin_version() -> str:
    payload = load_json(PLUGIN_MANIFEST_PATH)
    version = payload.get("version")
    if not isinstance(version, str) or not version.strip():
        raise ValueError(f"{PLUGIN_MANIFEST_PATH} is missing a valid version")
    return version
