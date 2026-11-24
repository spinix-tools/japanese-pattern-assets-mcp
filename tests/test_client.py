"""Call the catalog server over stdio as an MCP client would, and check the answers."""
import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

HERE = Path(__file__).parent


def payload(res):
    sc = getattr(res, "structured_content", None) or getattr(res, "structuredContent", None)
    if sc:
        return sc.get("result", sc) if isinstance(sc, dict) else sc
    texts = [c.text for c in res.content if getattr(c, "type", "") == "text"]
    try:
        return json.loads(texts[0]) if len(texts) == 1 else [json.loads(t) for t in texts]
    except Exception:
        return texts


async def main():
    params = StdioServerParameters(command=sys.executable, args=["-m", "japanese_pattern_assets_mcp"])
    ok = True
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            listed = (await s.list_tools()).tools
            tools = sorted(t.name for t in listed)
            ann = {t.name: (t.title, getattr(t.annotations, "read_only_hint", None) if t.annotations else None) for t in listed}
            print("annotations", ann)
            ok &= all(v[0] and v[1] is True for v in ann.values())
            print("tools", tools)
            ok &= tools == ["get_ai_use", "get_license", "get_link", "search_assets"]

            res = payload(await s.call_tool("search_assets", {"query": "seamless japanese pattern", "commercial_only": True}))
            ids = [x["id"] for x in res]
            print("search commercial", ids)
            ok &= "wagara-pattern-pack" in ids and "calendar-2027" not in ids

            res = payload(await s.call_tool("search_assets", {"query": "9-slice ui", "max_price_jpy": 0}))
            ids = [x["id"] for x in res]
            print("search free ui", ids)
            ok &= ids[0] == "japanese-ui-frames-free" and all(x != "japanese-ui-frames" for x in ids)

            res = payload(await s.call_tool("search_assets", {"query": "和柄", "no_ai_images": True}))
            print("search ja", [x["id"] for x in res])
            ok &= len(res) >= 3

            res = payload(await s.call_tool("search_assets", {"query": "", "use": "game-ui", "commercial_only": True}))
            ids = sorted(x["id"] for x in res)
            print("use game-ui", ids)
            ok &= "japanese-ui-frames" in ids and "calendar-2027" not in ids

            res = payload(await s.call_tool("search_assets", {"query": "pattern", "no_ai_at_all": True}))
            print("no AI at all", res)
            ok &= res == []

            res = payload(await s.call_tool("search_assets", {"query": "japanese textures", "no_ai_at_all": True}))
            print("no AI at all, textures", [x["id"] for x in res])
            ok &= set(x["id"] for x in res) == {"rekkimaru-japanese-textures-32", "phantomlucy-stylized-japanese-textures"}

            lic2 = payload(await s.call_tool("get_license", {"asset_id": "paulbarden-japanese-themed-tilesets"}))
            print("CC-BY credit", lic2.get("credit_required"))
            ok &= lic2.get("credit_required") is True

            res = payload(await s.call_tool("search_assets", {"query": "wave ui", "commercial_only": True}))
            print("commercial wave ui", [x["id"] for x in res])
            ok &= "puppetbomb-ui-wave" not in [x["id"] for x in res]

            for q in ["青海波", "seigaiha", "wave pattern"]:
                ids = [x["id"] for x in payload(await s.call_tool("search_assets", {"query": q, "commercial_only": True}))]
                print("pattern name", q, ids[:3])
                ok &= "wagara-pattern-pack" in ids
            ids = [x["id"] for x in payload(await s.call_tool("search_assets", {"query": "麻の葉", "kind": "asset-pack"}))]
            print("麻の葉 asset-pack", ids)
            ok &= "wagara-pattern-pack" in ids

            lic = payload(await s.call_tool("get_license", {"asset_id": "wagara-pixel-sampler"}))
            print("license sampler", lic.get("warning"))
            ok &= "warning" in lic

            ai = payload(await s.call_tool("get_ai_use", {"asset_id": "wagara-tile-maker"}))
            print("ai tile maker", ai.get("image"), ai.get("code"))
            ok &= ai.get("image") == "none" and ai.get("code") == "mostly"

            link = payload(await s.call_tool("get_link", {"asset_id": "japanese-ui-frames"}))
            print("link", link["url"], link["price"], link["how_to_get"])
            ok &= link["url"].startswith("https://spinix0.gumroad.com/l/ui-frames") and link["price"]["amount"] == 600

            bad = await s.call_tool("get_link", {"asset_id": "nope"})
            err = getattr(bad, "is_error", None) if hasattr(bad, "is_error") else getattr(bad, "isError", None)
            print("unknown id is error:", err)
            ok &= bool(err)
    print("ALL OK" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
