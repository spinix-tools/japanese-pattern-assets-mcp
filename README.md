# Japanese Pattern Assets MCP

An MCP server that lets AI agents (Claude, Cursor, Codex and others) find Japanese pattern assets — seamless tiles, game UI frames and printables — and check, before using them, the **license**, the **AI use** (self-declared, by step) and **where to get them**.

It never sells or downloads anything by itself. Free items point to their download page; paid items point to the store page (itch.io or Gumroad), where the human decides and buys. It makes no network calls: the catalog is a JSON file inside the package.

Version 0.2.7 — catalog checked 2026-11-24/25. 14 items: 9 by Spinix Tools, and 5 free Japanese-themed packs by other makers, listed by link only (files stay on the maker's page; follow the maker's license — some require credit, one is non-commercial only). Prices can change; the store page is always the source of truth.

## Tools

All four tools are read-only (annotated `readOnlyHint: true`).

| Tool | What it does |
| --- | --- |
| `search_assets` | Search by words (English or Japanese). Pattern names work in Japanese, romaji or English, e.g. 青海波 / seigaiha / wave, 麻の葉 / asanoha / hemp, 市松 / ichimatsu / checker. Each result has `matched`, showing which query words (and which other name) it matched. Filters: `kind` (tool / asset-pack / printable), `use` (game-ui, background, web, print, pixel-art, calendar, planner), `max_price_jpy` (0 = free only), `commercial_only`, `no_ai_images` (no image-generation AI), `no_ai_at_all` (no generative AI in any step), `no_credit_only` (no credit/attribution required; unknown is left out). |
| `get_license` | Commercial use, credit (and to whom), redistribution, and where the wording came from. Warns when a license still needs checking. |
| `get_ai_use` | Generative AI use per step (`none` / `assist` / `mostly`), plus the maker's statement. Self-declaration, not proof. |
| `get_link` | Store page, price, and how to get it. |

Example prompts: "Find a seamless Japanese wave pattern I can use commercially, no AI-generated images." / 「商用 OK の和柄の背景を探して。画像に生成 AI を使っていない物だけ」

## Example

Request to an agent: "I need Japanese-pattern UI frames for my Godot game. Commercial use, no AI-generated images."
These are real calls to v0.2.0 (run on 2026-11-24; v0.2.1 adds two more items, so results can include them); search results are shortened to a few fields.

1. `search_assets {"query": "japanese frame", "use": "game-ui", "commercial_only": true, "no_ai_images": true}`
   returns 5 items, free first:

   | id | price (JPY) | store | maker |
   | --- | --- | --- | --- |
   | japanese-ui-frames-free | 0 | Gumroad | Spinix Tools |
   | japanese-ui-frames | 600 | Gumroad | Spinix Tools |
   | wagara-tile-maker | 0 | itch.io | Spinix Tools |
   | rekkimaru-japanese-textures-32 | 0 | itch.io | Rekkimaru |
   | wagara-pattern-pack | 300 | itch.io | Spinix Tools |

2. `get_license {"asset_id": "japanese-ui-frames-free"}`
   → `"Free for your own games, free or commercial. Please do not resell or share the files as an asset pack."`, `commercial: true`, `credit_required: false`, source `Gumroad page, checked 2026-11-24`.

3. `get_ai_use {"asset_id": "japanese-ui-frames-free"}`
   → `image: none`, `devhelp: mostly`, `"Drawn in code; no image-generation AI. Code written with help from Claude."` (self-declaration, not a certification).

4. `get_link {"asset_id": "japanese-ui-frames-free"}`
   → `https://spinix0.gumroad.com/l/free-ui-frames`, price 0 JPY (pay what you want), `"Free: download from the store page."`

The agent then tells the human where to download it. For the paid 6-color pack, `get_link` returns the store page and the human decides whether to buy.

## Install

Requires Python 3.10+.

```bash
uvx --from git+https://github.com/spinix-tools/japanese-pattern-assets-mcp japanese-pattern-assets-mcp
```

Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "japanese-pattern-assets": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/spinix-tools/japanese-pattern-assets-mcp", "japanese-pattern-assets-mcp"]
    }
  }
}
```

Or with pip:

```bash
pip install git+https://github.com/spinix-tools/japanese-pattern-assets-mcp
japanese-pattern-assets-mcp
```

## About the AI-use field

Each item says, step by step, whether generative AI was used: images, code shipped in the item, behind-the-scenes code, text. For the Spinix Tools items the patterns are drawn by code from circles, lines and polygons — no image-generation AI — and the code was written with help from an AI assistant (Claude). This README and the server were also written by Claude.

`no_ai_at_all` returns only items declared to use no generative AI in any step; the Spinix Tools items are left out because their code was written with Claude, and items with no AI information (older pages) count as unknown and are left out too.

Some stores, game jams and asset bundles have their own AI rules. The field helps an agent filter, but it is the maker's self-declaration, not a certification, and not legal advice.

## Test

For development only: from a clone of this repository, install it in editable mode with pip (`pip install -e`, then a dot for the current folder) and run `python tests/test_client.py`. It starts the server over stdio and checks every tool.

## 日本語

AI（Claude・Cursor など）が、和柄の素材（継ぎ目のないタイル・ゲームの UI の枠・印刷用のカレンダーなど）を探し、使う前に**ライセンス**・**AI の使用**（工程ごとの自己申告）・**置き場所**を確かめられる MCP サーバーです。このサーバーは何も売らず、ダウンロードもしません。無料の物はダウンロードのページを、有料の物は売り場（itch.io・Gumroad）のページを返し、買うかどうかは人が決めます。外への通信はしません。

## Privacy Policy

This server collects nothing. It runs on your computer, reads only the catalog file inside the package, makes no network requests, keeps no logs of your queries, and shares nothing with Spinix Tools or anyone else. What your AI client does with the results is governed by that client's own policy. Questions: open an issue on this repository.

## License

Code: MIT. The catalog describes assets sold or shared under their own licenses; see each store page.
