# Japanese Pattern Assets MCP

An MCP server that lets AI agents (Claude, Cursor, Codex and others) find Japanese pattern assets — seamless tiles, game UI frames and printables — and check, before using them, the **license**, the **AI use** (self-declared, by step) and **where to get them**.

It never sells or downloads anything by itself. Free items point to their download page; paid items point to the store page (itch.io or Gumroad), where the human decides and buys. It makes no network calls: the catalog is a JSON file inside the package.

Version 0.1.0 — catalog checked 2026-11-24. 9 items, all by Spinix Tools. Prices can change; the store page is always the source of truth.

## Tools

| Tool | What it does |
| --- | --- |
| `search_assets` | Search by words (English or Japanese). Filters: `kind` (tool / asset-pack / printable), `max_price_jpy` (0 = free only), `commercial_only`, `no_ai_images`. |
| `get_license` | Commercial use, credit, redistribution, and where the wording came from. Warns when a license still needs checking. |
| `get_ai_use` | Generative AI use per step (`none` / `assist` / `mostly`), plus the maker's statement. Self-declaration, not proof. |
| `get_link` | Store page, price, and how to get it. |

Example prompts: "Find a seamless Japanese wave pattern I can use commercially, no AI-generated images." / 「商用 OK の和柄の背景を探して。画像に生成 AI を使っていない物だけ」

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

Or with pip: `pip install git+https://github.com/spinix-tools/japanese-pattern-assets-mcp` then run `japanese-pattern-assets-mcp`.

## About the AI-use field

Each item says, step by step, whether generative AI was used: images, code shipped in the item, behind-the-scenes code, text. For these items the patterns are drawn by code from circles, lines and polygons — no image-generation AI — and the code was written with help from an AI assistant (Claude). This README and the server were also written by Claude.

Some stores, game jams and asset bundles have their own AI rules. The field helps an agent filter, but it is the maker's self-declaration, not a certification, and not legal advice.

## Test

```bash
pip install -e .
python tests/test_client.py
```

## 日本語

AI（Claude・Cursor など）が、和柄の素材（継ぎ目のないタイル・ゲームの UI の枠・印刷用のカレンダーなど）を探し、使う前に**ライセンス**・**AI の使用**（工程ごとの自己申告）・**置き場所**を確かめられる MCP サーバーです。このサーバーは何も売らず、ダウンロードもしません。無料の物はダウンロードのページを、有料の物は売り場（itch.io・Gumroad）のページを返し、買うかどうかは人が決めます。外への通信はしません。

## License

Code: MIT. The catalog describes assets sold or shared under their own licenses; see each store page.
