#!/usr/bin/env python3
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path, PurePosixPath

from common import PLUGIN_ROOT, normalize_relpath


FORBIDDEN_TOP_LEVEL_FILES = {
    ".app.json",
    ".mcp.json",
    "README.md",
}
FORBIDDEN_PATH_PREFIXES = (
    ".codex-plugin/",
    ".github/",
    ".git/",
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify release-ready skill archives.")
    parser.add_argument("dist_dir", help="Directory containing skill zip artifacts")
    args = parser.parse_args()

    dist_dir = Path(args.dist_dir)
    archives = sorted(dist_dir.glob("*.zip"))
    errors: list[str] = []

    if not archives:
        errors.append(f"no zip archives found in {dist_dir}")

    for archive_path in archives:
        verify_archive(archive_path, errors)

    if errors:
        print("Archive verification failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print(f"Archive verification passed for {len(archives)} archive(s)")


def verify_archive(archive_path: Path, errors: list[str]) -> None:
    archive_skill_name = archive_path.name.rsplit("-v", 1)[0]
    source_skill_dir = PLUGIN_ROOT / "skills" / archive_skill_name
    if not source_skill_dir.is_dir():
        errors.append(f"{archive_path.name} does not map to an existing skill directory")
        return

    expected_files = {
        normalize_relpath(path, source_skill_dir)
        for path in sorted(source_skill_dir.rglob("*"))
        if path.is_file()
    }

    with zipfile.ZipFile(archive_path) as archive:
        actual_files = {
            name
            for name in archive.namelist()
            if not name.endswith("/")
        }

    if "SKILL.md" not in actual_files:
        errors.append(f"{archive_path.name} must contain SKILL.md at archive root")

    for name in sorted(actual_files):
        candidate = PurePosixPath(name)
        if candidate.is_absolute() or ".." in candidate.parts:
            errors.append(f"{archive_path.name} contains an invalid path `{name}`")
        if name in FORBIDDEN_TOP_LEVEL_FILES:
            errors.append(f"{archive_path.name} contains forbidden file `{name}`")
        if any(name.startswith(prefix) for prefix in FORBIDDEN_PATH_PREFIXES):
            errors.append(f"{archive_path.name} contains forbidden path `{name}`")

    if actual_files != expected_files:
        missing = sorted(expected_files - actual_files)
        extra = sorted(actual_files - expected_files)
        if missing:
            errors.append(f"{archive_path.name} is missing files: {', '.join(missing)}")
        if extra:
            errors.append(f"{archive_path.name} has unexpected files: {', '.join(extra)}")


if __name__ == "__main__":
    main()
