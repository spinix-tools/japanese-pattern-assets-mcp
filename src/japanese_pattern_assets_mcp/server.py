"""Japanese pattern assets for AI agents (Spinix Tools), v0.1.

An MCP server over stdio. It reads the catalog.json bundled with the package and
never connects to the network. Paid items are not sold here: get_link returns the
store page, where the human decides and buys.
"""
from __future__ import annotations

import json
import re
from importlib import resources

from mcp.server.mcpserver import MCPServer


def load_catalog() -> dict:
    text = resources.files(__package__ or "japanese_pattern_assets_mcp").joinpath("catalog.json").read_text(encoding="utf-8")
    return json.loads(text)


CATALOG = load_catalog()
ASSETS = {a["id"]: a for a in CATALOG["assets"]}

server = MCPServer(
    name="spinix-assets",
    instructions=(
        "Catalog of Japanese-pattern assets (tiles, game UI frames, printables) by Spinix Tools. "
        "Use search_assets to find items, get_license before using an item, get_ai_use when the user "
        "needs to know whether generative AI was used, and get_link to give the human the store page. "
        "Never claim an item was bought; paid items are bought by the human on the store page. "
        f"Catalog checked {CATALOG['checked']}; prices can change."
    ),
)


def _words(text: str) -> list[str]:
    return [w for w in re.split(r"[^0-9a-zA-Z぀-ヿ一-鿿-]+", text.lower()) if w]


def _haystack(a: dict) -> str:
    parts = [a.get("title", ""), a.get("title_ja", ""), a.get("kind", ""), a.get("contents", ""), a.get("preview", "")]
    parts += a.get("tags", []) + a.get("patterns", []) + a.get("formats", [])
    return " ".join(parts).lower()


def _summary(a: dict) -> dict:
    return {
        "id": a["id"],
        "title": a["title"],
        "kind": a["kind"],
        "price_jpy": a["price"]["amount"],
        "store": a["store"],
        "commercial_use": a["license"].get("commercial"),
        "image_generation_ai": a["ai_use"].get("image", "unknown"),
        "formats": a.get("formats", []),
    }


@server.tool()
def search_assets(
    query: str,
    kind: str | None = None,
    max_price_jpy: int | None = None,
    commercial_only: bool = False,
    no_ai_images: bool = False,
    limit: int = 10,
) -> list[dict]:
    """Search the catalog.

    query: words to match (English or Japanese), e.g. "seamless japanese pattern" or "9-slice ui".
    kind: "tool", "asset-pack" or "printable" to narrow.
    max_price_jpy: 0 for free items only.
    commercial_only: only items whose license allows commercial use (unknown licenses are left out).
    no_ai_images: only items whose images were not made with image-generation AI.
    """
    words = _words(query)
    scored = []
    for a in CATALOG["assets"]:
        if kind and a["kind"] != kind:
            continue
        if max_price_jpy is not None and a["price"]["amount"] > max_price_jpy:
            continue
        if commercial_only and a["license"].get("commercial") is not True:
            continue
        if no_ai_images and a["ai_use"].get("image") != "none":
            continue
        hay = _haystack(a)
        score = sum(1 for w in words if w in hay)
        if words and score == 0:
            continue
        scored.append((score, a))
    scored.sort(key=lambda x: (-x[0], x[1]["price"]["amount"]))
    return [_summary(a) for _, a in scored[: max(1, min(limit, 50))]]


def _get(asset_id: str) -> dict:
    if asset_id not in ASSETS:
        raise ValueError(f"unknown asset id: {asset_id}. Use search_assets to find ids.")
    return ASSETS[asset_id]


@server.tool()
def get_license(asset_id: str) -> dict:
    """License of one item: commercial use, credit, redistribution, and where the wording came from."""
    a = _get(asset_id)
    lic = dict(a["license"])
    lic["id"] = asset_id
    lic["checked"] = CATALOG["checked"]
    if lic.get("source") == "要確認":
        lic["warning"] = "License not re-read on the live page. Ask the human to check the store page before use."
    return lic


@server.tool()
def get_ai_use(asset_id: str) -> dict:
    """Self-declared generative AI use, by step (none / assist / mostly). Not proof."""
    a = _get(asset_id)
    out = dict(a["ai_use"])
    out["id"] = asset_id
    out["note"] = "Self-declaration by the maker, following the AI Use Label steps. Not a certification."
    return out


@server.tool()
def get_link(asset_id: str) -> dict:
    """Store page for the human. Paid items are bought there by the human, not by the agent."""
    a = _get(asset_id)
    price = a["price"]
    return {
        "id": asset_id,
        "title": a["title"],
        "url": a["url"],
        "store": a["store"],
        "price": price,
        "how_to_get": "Free: download from the store page." if price["amount"] == 0 else "Paid: the human opens the store page and decides whether to buy.",
        "checked": CATALOG["checked"],
    }


def main() -> None:
    server.run("stdio")


if __name__ == "__main__":
    main()
