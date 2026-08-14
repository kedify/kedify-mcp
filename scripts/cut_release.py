#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys

from common import SEMVER_RE


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Cut a kedify-mcp release by stamping plugin.json, validating, "
            "committing the version bump, creating a tag, and optionally pushing."
        )
    )
    parser.add_argument("--version", required=True, help="Release version without the leading v")
    parser.add_argument(
        "--push",
        action="store_true",
        help="Push the current branch and release tag after creating them locally",
    )
    parser.add_argument(
        "--remote",
        default="origin",
        help="Git remote to push to when --push is used (default: origin)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the actions that would run without changing git state",
    )
    args = parser.parse_args()

    version = args.version.strip()
    if SEMVER_RE.fullmatch(version) is None:
        raise SystemExit(f"Version `{version}` is not valid semver")
    tag_name = f"v{version}"

    ensure_clean_worktree()
    ensure_tag_missing(tag_name)

    if args.dry_run:
        print(f"Would set plugin.json version to {version}")
        print(f"Would validate plugin and skills for {tag_name}")
        print(f"Would commit .codex-plugin/plugin.json with message: release: {tag_name}")
        print(f"Would create annotated tag: {tag_name}")
        if args.push:
            branch = git_output("rev-parse", "--abbrev-ref", "HEAD")
            print(f"Would push branch `{branch}` and tag `{tag_name}` to `{args.remote}`")
        return

    run_python_script("scripts/set_plugin_version.py", "--version", version)
    run_python_script("scripts/validate_plugin.py", "--expected-version", version)
    run_python_script("scripts/validate_skills.py")
    run_python_script("scripts/build_skill_archives.py", "--version", version, "--out", "dist")
    run_python_script("scripts/verify_archives.py", "dist")

    git("add", ".codex-plugin/plugin.json")
    git("commit", "-m", f"release: {tag_name}")
    git("tag", "-a", tag_name, "-m", tag_name)

    print(f"Created release commit and tag {tag_name}")

    if args.push:
        branch = git_output("rev-parse", "--abbrev-ref", "HEAD")
        git("push", args.remote, branch)
        git("push", args.remote, tag_name)
        print(f"Pushed branch `{branch}` and tag `{tag_name}` to `{args.remote}`")
    else:
        print(f"Next step: git push origin HEAD && git push origin {tag_name}")


def ensure_clean_worktree() -> None:
    status = git_output("status", "--short")
    if status:
        raise SystemExit(
            "Refusing to cut a release from a dirty worktree.\n"
            "Commit or stash your changes first, then rerun the release command."
        )


def ensure_tag_missing(tag_name: str) -> None:
    result = subprocess.run(
        ["git", "rev-parse", "-q", "--verify", f"refs/tags/{tag_name}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        raise SystemExit(f"Git tag `{tag_name}` already exists")


def run_python_script(script: str, *script_args: str) -> None:
    cmd = [sys.executable, script, *script_args]
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def git(*git_args: str) -> None:
    cmd = ["git", *git_args]
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def git_output(*git_args: str) -> str:
    result = subprocess.run(
        ["git", *git_args],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


if __name__ == "__main__":
    main()
