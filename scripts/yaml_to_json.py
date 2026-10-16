#!/usr/bin/env python
"""Generate themes.json from themes.yaml.

The JSON twin of themes.yaml, for consumers that read a palette without a
YAML parser: rssite templates (`load_data`), Rust tools such as rsslide,
Lua filters. Themes are a list so the switcher order is the file order:

    {
      "default": "azure",
      "base": {"radius": "10px", ...},
      "themes": [
        {"code": "azure", "label": "Azure", "description": "cool light, indigo",
         "tokens": {"bg": "#ffffff", ...}},
        ...
      ]
    }
"""

from __future__ import annotations

import json
import sys

from themes_common import ROOT, load_themes

JSON_PATH = ROOT / "themes.json"


def main() -> int:
    data = load_themes()
    doc = {
        "default": data.default,
        "base": data.base,
        "themes": [
            {
                "code": code,
                "label": data.labels[code],
                "description": data.descriptions[code],
                "tokens": tokens,
            }
            for code, tokens in data.themes.items()
        ],
    }
    JSON_PATH.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {JSON_PATH.relative_to(ROOT)} ({len(data.themes)} themes, default={data.default})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
