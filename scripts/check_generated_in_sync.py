#!/usr/bin/env python3
"""Fail the build when a committed generated file differs from what the
generators just produced from themes.yaml.

The build regenerates themes.css, theme.py and manim_themes.py into the
working tree. If the committed copies are stale, `git diff` reports them and
this check fails, so drift between themes.yaml and its generated artifacts is
caught in CI instead of silently shipping.

Usage: check_generated_in_sync.py <stamp> <generated files...>
"""

import os
import subprocess
import sys


def main() -> None:
    stamp, files = sys.argv[1], sys.argv[2:]
    result = subprocess.run(
        ["git", "diff", "--exit-code", "--stat", "--", *files],
        check=False,
    )
    if result.returncode != 0:
        print("generated files are out of sync with themes.yaml; commit the regenerated files", file=sys.stderr)
        sys.exit(result.returncode)
    os.makedirs(os.path.dirname(stamp), exist_ok=True)
    with open(stamp, "w", encoding="utf-8") as handle:
        handle.write("ok\n")


if __name__ == "__main__":
    main()
