import httpx

async def get_country(ip: str) -> str:
    if ip in ("127.0.0.1", "::1", "testclient"):
        return "US"
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            r = await client.get(f"http://ip-api.com/json/{ip}?fields=countryCode")
            data = r.json()
            return data.get("countryCode", "XX")
    except Exception:
        return "XX"

def get_device(user_agent: str) -> str:
    ua = user_agent.lower()
    if any(x in ua for x in ["iphone", "android", "mobile"]):
        return "mobile"
    if "tablet" in ua or "ipad" in ua:
        return "tablet"
    return "desktop"