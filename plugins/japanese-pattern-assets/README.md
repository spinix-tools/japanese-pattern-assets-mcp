# Japanese Pattern Assets (Claude plugin)

Find Japanese pattern and Japanese-themed assets with Claude — seamless wagara tiles (seigaiha, asanoha, ichimatsu and more), game UI frames, textures and printable calendars — and check each item's license and generative-AI use before you use it.

## Install

In Claude Code, in one step (Claude Code 2.1.275 or later):

```
/plugin install japanese-pattern-assets --marketplace spinix-tools/japanese-pattern-assets-mcp
```

Or add the marketplace first, then install:

```
/plugin marketplace add spinix-tools/japanese-pattern-assets-mcp
/plugin install japanese-pattern-assets@spinix-tools
```

The marketplace is a file in the public GitHub repository spinix-tools/japanese-pattern-assets-mcp; adding it needs `git` on your computer.

## Use it

Ask, for example: "Find Japanese-pattern UI frames for my Godot game. Commercial use, no AI-generated images." Claude searches the catalog, checks the license (commercial use, credit, redistribution) and the maker's AI-use declaration, and gives you the store page. Free items download from that page; paid items are bought by you on the store page.

The plugin has one skill and one local MCP server (`server.py`, Python standard library only, started with `python3`). In Claude Code and Cowork on your computer, the server runs from the plugin folder; nothing is downloaded or installed. In chat, the skill reads the same catalog bundled in the plugin.

## Data

The plugin sends nothing anywhere and fetches nothing. The MCP server runs on your computer, reads only the bundled catalog (`skills/find-japanese-pattern-assets/references/catalog.json`), and makes no network requests. Nothing is stored or logged. It needs Python 3.8 or later.

## Privacy Policy

Spinix Tools collects no data through this plugin: no queries, no usage data, no personal data. Questions: open an issue at https://github.com/spinix-tools/japanese-pattern-assets-mcp/issues

## License

MIT. The catalog describes assets that are sold or shared under their own licenses; see each store page.
