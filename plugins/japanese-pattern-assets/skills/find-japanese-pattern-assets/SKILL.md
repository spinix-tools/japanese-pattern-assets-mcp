---
name: find-japanese-pattern-assets
description: Find Japanese pattern or Japanese-themed assets (seamless wagara tiles such as seigaiha, asanoha, ichimatsu; game UI frames; textures; printable calendars) and check license and AI use. Use when the user wants Japanese patterns or wa-style assets for a game, website, print or product, or asks whether an asset allows commercial use or was made with generative AI.
---

To find an asset:

1. If the `japanese-pattern-assets` connector's tools are available, call `search_assets` with the user's words and conditions: `use` (game-ui, background, web, print, pixel-art, calendar, planner), `commercial_only`, `no_ai_images` (no image-generation AI) or `no_ai_at_all` (no generative AI in any step), `max_price_jpy` (0 for free only). Pattern names work in Japanese, romaji or English (青海波 / seigaiha / wave).
2. If the tools are not available, read `references/catalog.json` and apply the same conditions yourself.
3. Before recommending an item, check its license (`get_license`, or the item's `license` in the catalog). Say plainly if credit is required, if commercial use is not stated, or if the source is marked 要確認 (needs checking).
4. If the user cares about AI, report the item's `ai_use` per step. It is the maker's self-declaration, not proof. Keep "none" and "unknown" apart: an item with no AI information is unknown, not AI-free.
5. Give the store link (`get_link`, or the item's `url`). Free items are downloaded from that page. For paid items, the person decides and buys on the store page; never say an item was bought.

Prices and license wording were checked on the date in the catalog (`checked`). Tell the user to confirm on the store page before using an item in a released product.
