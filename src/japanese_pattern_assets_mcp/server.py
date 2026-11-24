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
from mcp.types import ToolAnnotations

READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)


def load_catalog() -> dict:
    text = resources.files(__package__ or "japanese_pattern_assets_mcp").joinpath("catalog.json").read_text(encoding="utf-8")
    return json.loads(text)


CATALOG = load_catalog()
ASSETS = {a["id"]: a for a in CATALOG["assets"]}

server = MCPServer(
    name="spinix-assets",
    instructions=(
        "Catalog of Japanese-pattern and Japanese-themed assets (tiles, game UI frames, textures, tilesets, printables) "
        "by Spinix Tools and, link only, by other makers. "
        "Use search_assets to find items, get_license before using an item, get_ai_use when the user "
        "needs to know whether generative AI was used, and get_link to give the human the store page. "
        "Never claim an item was bought; paid items are bought by the human on the store page. "
        f"Catalog checked {CATALOG['checked']}; prices can change."
    ),
)


# Same pattern, different names (Japanese, romaji, English). A query word that
# matches any name in a group also searches for the other names in that group.
PATTERN_NAMES = [
    ["seigaiha", "青海波", "せいがいは", "wave", "waves"],
    ["asanoha", "麻の葉", "あさのは", "hemp"],
    ["shippo", "七宝", "しっぽう", "shippou"],
    ["kikko", "亀甲", "きっこう", "tortoise", "hexagon", "hexagonal"],
    ["kagome", "籠目", "かごめ", "basket"],
    ["sayagata", "紗綾形", "さやがた", "key-fret", "fret"],
    ["uroko", "鱗", "うろこ", "scales", "scale"],
    ["ichimatsu", "市松", "いちまつ", "checker", "checkerboard", "checkered"],
    ["yagasuri", "矢絣", "やがすり", "arrow", "arrows"],
    ["wagara", "和柄", "わがら", "japanese-pattern"],
]
_NAME_INDEX = {name.lower(): group for group in PATTERN_NAMES for name in group}


def _expand(words: list[str]) -> list[set[str]]:
    """Each query word becomes a set of alternatives (itself plus its other names)."""
    return [set(n.lower() for n in _NAME_INDEX.get(w, [w])) | {w} for w in words]


def _words(text: str) -> list[str]:
    return [w for w in re.split(r"[^0-9a-zA-Z぀-ヿ一-鿿-]+", text.lower()) if w]


def _haystack(a: dict) -> str:
    parts = [a.get("title", ""), a.get("title_ja", ""), a.get("kind", ""), a.get("contents", ""), a.get("preview", ""), a.get("maker", "")]
    parts += a.get("tags", []) + a.get("patterns", []) + a.get("formats", [])
    return " ".join(parts).lower()


def _ai_image(a: dict) -> str:
    ai = a.get("ai_use", {})
    return ai.get("image") or ai.get("all") or "unknown"


def _no_ai_anywhere(a: dict) -> bool:
    ai = a.get("ai_use", {})
    if ai.get("all") == "none":
        return True
    steps = {k: v for k, v in ai.items() if k not in ("statement", "itch_disclosure", "all")}
    return bool(steps) and all(v == "none" for v in steps.values())


def _summary(a: dict) -> dict:
    return {
        "id": a["id"],
        "title": a["title"],
        "kind": a["kind"],
        "price_jpy": a["price"]["amount"],
        "store": a["store"],
        "commercial_use": a["license"].get("commercial"),
        "maker": a.get("maker", ""),
        "image_generation_ai": _ai_image(a),
        "credit_required": a["license"].get("credit_required"),
        "formats": a.get("formats", []),
        "uses": a.get("uses", []),
    }


@server.tool(title="Search assets", annotations=READ_ONLY)
def search_assets(
    query: str,
    kind: str | None = None,
    max_price_jpy: int | None = None,
    commercial_only: bool = False,
    no_ai_images: bool = False,
    use: str | None = None,
    no_ai_at_all: bool = False,
    limit: int = 10,
) -> list[dict]:
    """Search the catalog.

    query: words to match (English or Japanese), e.g. "seamless japanese pattern" or "9-slice ui".
    kind: "tool", "asset-pack" or "printable" to narrow.
    max_price_jpy: 0 for free items only.
    commercial_only: only items whose license allows commercial use (unknown licenses are left out).
    no_ai_images: only items whose images were not made with image-generation AI.
    use: what it is for, e.g. "game-ui", "background", "web", "print", "pixel-art", "calendar", "planner".
    no_ai_at_all: only items declared to use no generative AI in any step. Items with unknown AI use are left out.
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
        if no_ai_images and _ai_image(a) != "none":
            continue
        if use and use.lower() not in [u.lower() for u in a.get("uses", [])]:
            continue
        if no_ai_at_all and not _no_ai_anywhere(a):
            continue
        hay = _haystack(a)
        matched = []
        for w, alts in zip(words, _expand(words)):
            hit = next((alt for alt in sorted(alts) if alt in hay), None)
            if hit:
                matched.append(w if hit == w else f"{w} ({hit})")
        if words and not matched:
            continue
        scored.append((len(matched), matched, a))
    scored.sort(key=lambda x: (-x[0], x[2]["price"]["amount"]))
    return [dict(_summary(a), matched=m) for _, m, a in scored[: max(1, min(limit, 50))]]


def _get(asset_id: str) -> dict:
    if asset_id not in ASSETS:
        raise ValueError(f"unknown asset id: {asset_id}. Use search_assets to find ids.")
    return ASSETS[asset_id]


@server.tool(title="Get license", annotations=READ_ONLY)
def get_license(asset_id: str) -> dict:
    """License of one item: commercial use, credit, redistribution, and where the wording came from."""
    a = _get(asset_id)
    lic = dict(a["license"])
    lic["id"] = asset_id
    lic["checked"] = CATALOG["checked"]
    if lic.get("source") == "要確認":
        lic["warning"] = "License not confirmed on the store page. Ask the human to check it before use."
    return lic


@server.tool(title="Get AI use", annotations=READ_ONLY)
def get_ai_use(asset_id: str) -> dict:
    """Self-declared generative AI use, by step (none / assist / mostly). Not proof."""
    a = _get(asset_id)
    out = dict(a["ai_use"])
    out["id"] = asset_id
    out["note"] = "Self-declaration by the maker, following the AI Use Label steps. Not a certification."
    return out


@server.tool(title="Get store link", annotations=READ_ONLY)
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
