#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path

from common import discover_skill_dirs, normalize_relpath, plugin_version


def main() -> None:
    parser = argparse.ArgumentParser(description="Build ChatGPT-upload skill archives.")
    parser.add_argument("--out", default="dist", help="Output directory for zip artifacts")
    parser.add_argument(
        "--version",
        help="Version suffix for archive names. Defaults to plugin.json version.",
    )
    args = parser.parse_args()

    version = args.version or plugin_version()
    out_dir = Path(args.out)
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    archives: list[Path] = []
    for skill_dir in discover_skill_dirs():
        archive_path = out_dir / f"{skill_dir.name}-v{version}.zip"
        build_archive(skill_dir, archive_path)
        archives.append(archive_path)

    if not archives:
        raise SystemExit("No skills found to archive")

    print("Built skill archives:")
    for archive_path in archives:
        print(f"- {archive_path}")


def build_archive(skill_dir: Path, archive_path: Path) -> None:
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(skill_dir.rglob("*")):
            if path.is_dir():
                continue
            archive.write(path, arcname=normalize_relpath(path, skill_dir))


if __name__ == "__main__":
    main()
