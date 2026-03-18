from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from api.database import get_db
from api.models import Link, Click, Rule
from api.services.geoip import get_country, get_device
from api.services.rule_engine import evaluate_rules
from api.services.ab_test import get_ab_variant
from api.services.cache import get_cached_link, cache_link
from api.services.ratelimit import is_rate_limited
from datetime import datetime, timezone
import asyncio

router = APIRouter()

@router.get("/{short_code}")
async def redirect(short_code: str, request: Request, db: Session = Depends(get_db)):
    ip = request.client.host

    if is_rate_limited(ip):
        raise HTTPException(status_code=429, detail="Too many requests")

    cached = get_cached_link(short_code)
    if cached:
        target_url = cached["default_url"]
        link_id = cached["id"]
        country = await get_country(ip)
        device = get_device(request.headers.get("user-agent", ""))
        referrer = request.headers.get("referer", "")
        asyncio.create_task(log_click(db, link_id, country, device, referrer, None, None))
        return RedirectResponse(url=target_url, status_code=302)

    link = db.query(Link).filter(Link.short_code == short_code).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    if link.expires_at and datetime.now(timezone.utc) > link.expires_at.replace(tzinfo=timezone.utc):
        raise HTTPException(status_code=410, detail="Link has expired")

    cache_link(short_code, {"id": link.id, "default_url": link.default_url})

    ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    referrer = request.headers.get("referer", "")

    country = await get_country(ip)
    device = get_device(user_agent)

    matched_rule_id = None
    ab_variant = None

    if link.is_ab_test and link.ab_url_b:
        target_url, ab_variant = get_ab_variant(link, ip)
    else:
        rule_url = evaluate_rules(link.rules, country, device, referrer)
        if rule_url:
            matched_rule = next((r for r in link.rules if r.target_url == rule_url), None)
            matched_rule_id = matched_rule.id if matched_rule else None
            target_url = rule_url
        else:
            target_url = link.default_url

    asyncio.create_task(log_click(
        db, link.id, country, device, referrer, matched_rule_id, ab_variant
    ))

    return RedirectResponse(url=target_url, status_code=302)


async def log_click(db, link_id, country, device, referrer, matched_rule_id, ab_variant):
    try:
        click = Click(
            link_id=link_id,
            country=country,
            device=device,
            referrer=referrer,
            matched_rule_id=matched_rule_id,
            ab_variant=ab_variant,
        )
        db.add(click)
        db.commit()
    except Exception:
        db.rollback()