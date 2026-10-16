#!/usr/bin/env python3
"""Fail the build when a committed generated file differs from what the
generators just produced from themes.yaml and diagram-themes.yaml.

The build regenerates the artifacts (themes.css, themes.json, theme.py,
manim_themes.py, marp/*.css, diagram_theme.py) into the working tree. If a
committed copy is stale, `git diff` reports it and this check fails; if a
generated file is not tracked at all (a new theme's marp file, say), `git
ls-files` reports it and the check fails too. Drift between a YAML source
and its generated artifacts is caught in CI instead of silently shipping.

Usage: check_generated_in_sync.py <stamp> <generated files...>

rsconstruct appends `--inputs ...` and `--output-files ...` after the
configured args, so the file list ends at the first flag.
"""

import os
import subprocess
import sys


def main() -> None:
    stamp, rest = sys.argv[1], sys.argv[2:]
    files = []
    for arg in rest:
        if arg.startswith("--"):
            break
        files.append(arg)
    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "--", *files],
        check=False,
        capture_output=True,
        text=True,
    )
    if tracked.returncode != 0:
        print(tracked.stderr, end="", file=sys.stderr)
        print("generated files are not tracked by git; add them", file=sys.stderr)
        sys.exit(tracked.returncode)
    result = subprocess.run(
        ["git", "diff", "--exit-code", "--stat", "--", *files],
        check=False,
    )
    if result.returncode != 0:
        print("generated files are out of sync with their YAML sources; commit the regenerated files", file=sys.stderr)
        sys.exit(result.returncode)
    os.makedirs(os.path.dirname(stamp), exist_ok=True)
    with open(stamp, "w", encoding="utf-8") as handle:
        handle.write("ok\n")


if __name__ == "__main__":
    main()
