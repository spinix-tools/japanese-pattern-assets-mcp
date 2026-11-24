#!/usr/bin/env python3
"""Japanese Pattern Assets: a small MCP server that uses only the Python standard library.

It speaks JSON-RPC 2.0 over stdio (one JSON message per line), reads the catalog
bundled at skills/find-japanese-pattern-assets/references/catalog.json, and never
opens a network connection. Paid items are not sold here: get_link returns the
store page, where the person decides and buys.
"""
from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CATALOG_PATH = os.path.join(HERE, "skills", "find-japanese-pattern-assets", "references", "catalog.json")
SERVER_NAME = "japanese-pattern-assets"
SERVER_VERSION = "0.3.1"
SUPPORTED_PROTOCOLS = ["2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05"]

with open(CATALOG_PATH, encoding="utf-8") as f:
    CATALOG = json.load(f)
ASSETS = {a["id"]: a for a in CATALOG["assets"]}

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
NAME_INDEX = {n.lower(): g for g in PATTERN_NAMES for n in g}

INSTRUCTIONS = (
    "Catalog of Japanese-pattern and Japanese-themed assets (tiles, game UI frames, textures, tilesets, printables) "
    "by Spinix Tools and, link only, by other makers. Use search_assets to find items, get_license before using an item, "
    "get_ai_use when the user needs to know whether generative AI was used, and get_link to give the person the store page. "
    "Never claim an item was bought; paid items are bought by the person on the store page. "
    f"Catalog checked {CATALOG.get('checked', '')}; prices can change."
)

READ_ONLY = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
ID_SCHEMA = {"type": "object", "properties": {"asset_id": {"type": "string", "description": "id from search_assets"}}, "required": ["asset_id"]}
TOOLS = [
    {
        "name": "search_assets",
        "title": "Search assets",
        "description": (
            "Search the catalog by words (English or Japanese; pattern names work in Japanese, romaji or English, "
            "e.g. 青海波 / seigaiha / wave). Filters: kind (tool, asset-pack, printable), use (game-ui, background, web, "
            "print, pixel-art, calendar, planner), max_price_jpy (0 = free only), commercial_only, no_ai_images "
            "(no image-generation AI), no_ai_at_all (no generative AI in any step; unknown AI use is left out), "
            "no_credit_only (no credit/attribution required; unknown is left out)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "kind": {"type": "string"},
                "use": {"type": "string"},
                "max_price_jpy": {"type": "integer"},
                "commercial_only": {"type": "boolean", "default": False},
                "no_ai_images": {"type": "boolean", "default": False},
                "no_ai_at_all": {"type": "boolean", "default": False},
                "no_credit_only": {"type": "boolean", "default": False},
                "limit": {"type": "integer", "default": 10},
            },
            "required": ["query"],
        },
        "annotations": READ_ONLY,
    },
    {"name": "get_license", "title": "Get license", "description": "License of one item: commercial use, credit, redistribution, and where the wording came from. Warns when it still needs checking.", "inputSchema": ID_SCHEMA, "annotations": READ_ONLY},
    {"name": "get_ai_use", "title": "Get AI use", "description": "Self-declared generative AI use by step (none / assist / mostly). Not proof. Unknown is kept apart from none.", "inputSchema": ID_SCHEMA, "annotations": READ_ONLY},
    {"name": "get_link", "title": "Get store link", "description": "Store page, price and how to get the item. Paid items are bought there by the person, not by the agent.", "inputSchema": ID_SCHEMA, "annotations": READ_ONLY},
]


def words(text: str) -> list[str]:
    return [w for w in re.split(r"[^0-9a-zA-Z぀-ヿ一-鿿-]+", text.lower()) if w]


def expand(ws: list[str]) -> list[set[str]]:
    return [set(n.lower() for n in NAME_INDEX.get(w, [w])) | {w} for w in ws]


def haystack(a: dict) -> str:
    parts = [a.get(k, "") for k in ("title", "title_ja", "kind", "contents", "preview", "maker")]
    parts += a.get("tags", []) + a.get("patterns", []) + a.get("formats", []) + a.get("uses", [])
    return " ".join(parts).lower()


def ai_image(a: dict) -> str:
    ai = a.get("ai_use", {})
    return ai.get("image") or ai.get("all") or "unknown"


def no_ai_anywhere(a: dict) -> bool:
    ai = a.get("ai_use", {})
    if ai.get("all") == "none":
        return True
    steps = {k: v for k, v in ai.items() if k not in ("statement", "itch_disclosure", "all", "note")}
    return bool(steps) and all(v == "none" for v in steps.values())


def summary(a: dict) -> dict:
    return {
        "id": a["id"], "title": a["title"], "kind": a["kind"], "price": a["price"], "store": a["store"],
        "maker": a.get("maker", ""), "commercial_use": a["license"].get("commercial"),
        "credit_required": a["license"].get("credit_required"), "image_generation_ai": ai_image(a),
        "formats": a.get("formats", []), "uses": a.get("uses", []),
    }


def search_assets(args: dict) -> list[dict]:
    query = str(args.get("query", ""))
    kind, use = args.get("kind"), args.get("use")
    max_price = args.get("max_price_jpy")
    ws = words(query)
    scored = []
    for a in CATALOG["assets"]:
        price = a["price"]
        if kind and a["kind"] != kind:
            continue
        if max_price is not None:
            if price.get("currency") == "JPY":
                if price["amount"] > max_price:
                    continue
            elif price["amount"] > 0:  # other currencies are not converted; with a price limit only free ones pass
                continue
        if args.get("commercial_only") and a["license"].get("commercial") is not True:
            continue
        if args.get("no_ai_images") and ai_image(a) != "none":
            continue
        if use and use.lower() not in [u.lower() for u in a.get("uses", [])]:
            continue
        if args.get("no_ai_at_all") and not no_ai_anywhere(a):
            continue
        if args.get("no_credit_only") and a["license"].get("credit_required") is not False:
            continue
        hay = haystack(a)
        matched = []
        for w, alts in zip(ws, expand(ws)):
            hit = next((x for x in sorted(alts) if x in hay), None)
            if hit:
                matched.append(w if hit == w else f"{w} ({hit})")
        if ws and not matched:
            continue
        scored.append((len(matched), matched, a))
    scored.sort(key=lambda x: (-x[0], x[2]["price"]["amount"]))
    limit = max(1, min(int(args.get("limit", 10) or 10), 50))
    return [dict(summary(a), matched=m) for _, m, a in scored[:limit]]


def get_asset(args: dict) -> dict:
    asset_id = str(args.get("asset_id", ""))
    if asset_id not in ASSETS:
        raise ValueError(f"unknown asset id: {asset_id}. Use search_assets to find ids.")
    return ASSETS[asset_id]


def get_license(args: dict) -> dict:
    a = get_asset(args)
    out = dict(a["license"], id=a["id"], checked=CATALOG.get("checked"))
    if out.get("source") == "要確認":
        out["warning"] = "License not confirmed on the store page. Ask the person to check it before use."
    return out


def get_ai_use(args: dict) -> dict:
    a = get_asset(args)
    return dict(a["ai_use"], id=a["id"], note="Self-declaration by the maker, not a certification.")


def get_link(args: dict) -> dict:
    a = get_asset(args)
    free = a["price"]["amount"] == 0
    return {
        "id": a["id"], "title": a["title"], "url": a["url"], "store": a["store"], "price": a["price"],
        "how_to_get": "Free: download from the store page." if free else "Paid: the person opens the store page and decides whether to buy.",
        "checked": CATALOG.get("checked"),
    }


HANDLERS = {"search_assets": search_assets, "get_license": get_license, "get_ai_use": get_ai_use, "get_link": get_link}


def call_tool(params: dict) -> dict:
    name = params.get("name")
    args = params.get("arguments") or {}
    if name not in HANDLERS:
        return {"content": [{"type": "text", "text": f"unknown tool: {name}"}], "isError": True}
    try:
        result = HANDLERS[name](args)
    except Exception as e:  # report tool errors to the model, not as protocol errors
        return {"content": [{"type": "text", "text": str(e)}], "isError": True}
    text = json.dumps(result, ensure_ascii=False)
    out = {"content": [{"type": "text", "text": text}], "isError": False}
    out["structuredContent"] = {"result": result} if isinstance(result, list) else result
    return out


def handle(msg: dict) -> dict | None:
    method, mid, params = msg.get("method"), msg.get("id"), msg.get("params") or {}
    if mid is None:  # notification
        return None
    if method == "initialize":
        asked = params.get("protocolVersion")
        version = asked if asked in SUPPORTED_PROTOCOLS else SUPPORTED_PROTOCOLS[0]
        result = {
            "protocolVersion": version,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            "instructions": INSTRUCTIONS,
        }
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        result = call_tool(params)
    else:
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"Method not found: {method}"}}
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
        else:
            reply = handle(msg) if isinstance(msg, dict) else {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Invalid Request"}}
        if reply is not None:
            sys.stdout.write(json.dumps(reply, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
