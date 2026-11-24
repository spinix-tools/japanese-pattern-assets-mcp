"""Copy the one catalog (the Python package's) into the Claude plugin, and check they match.

The source of truth is src/japanese_pattern_assets_mcp/catalog.json. The plugin keeps a copy at
plugins/japanese-pattern-assets/skills/find-japanese-pattern-assets/references/catalog.json, because a
plugin is installed as its own folder. Run this after every catalog change, then raise "version" in
plugins/japanese-pattern-assets/.claude-plugin/plugin.json so installed copies get the update.

    python scripts/sync_plugin_catalog.py          # copy
    python scripts/sync_plugin_catalog.py --check  # exit 1 if they differ (for tests)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "japanese_pattern_assets_mcp" / "catalog.json"
DST = ROOT / "plugins" / "japanese-pattern-assets" / "skills" / "find-japanese-pattern-assets" / "references" / "catalog.json"


def main() -> int:
    same = DST.exists() and DST.read_bytes() == SRC.read_bytes()
    if "--check" in sys.argv:
        print("plugin catalog matches" if same else "plugin catalog differs: run scripts/sync_plugin_catalog.py")
        return 0 if same else 1
    if same:
        print("already the same")
        return 0
    DST.write_bytes(SRC.read_bytes())
    print("copied; now raise the version in plugins/japanese-pattern-assets/.claude-plugin/plugin.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
