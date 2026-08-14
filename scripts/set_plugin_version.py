#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from common import PLUGIN_MANIFEST_PATH, SEMVER_RE, load_json


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Set .codex-plugin/plugin.json version to a specific release value."
    )
    parser.add_argument("--version", required=True, help="Semver version to write")
    args = parser.parse_args()

    version = args.version.strip()
    if SEMVER_RE.fullmatch(version) is None:
        raise SystemExit(f"Version `{version}` is not valid semver")

    payload = load_json(PLUGIN_MANIFEST_PATH)
    if not isinstance(payload, dict):
        raise SystemExit(f"{PLUGIN_MANIFEST_PATH} must contain a JSON object")

    old_version = payload.get("version")
    payload["version"] = version
    with PLUGIN_MANIFEST_PATH.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")

    if old_version == version:
        print(f"Plugin version already set to {version}")
    else:
        print(f"Updated plugin version from {old_version!r} to {version!r}")


if __name__ == "__main__":
    main()
