from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import get_db
from api.models import Link, Click

router = APIRouter()

@router.get("/links/{short_code}/analytics")
def get_analytics(short_code: str, token: str, db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.short_code == short_code).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    if link.manage_token != token:
        raise HTTPException(status_code=403, detail="Invalid manage token")

    clicks = db.query(Click).filter(Click.link_id == link.id).all()

    by_country = {}
    by_device = {}
    by_date = {}
    ab_variants = {"A": 0, "B": 0}

    for click in clicks:
        country = click.country or "XX"
        by_country[country] = by_country.get(country, 0) + 1

        device = click.device or "unknown"
        by_device[device] = by_device.get(device, 0) + 1

        date_str = click.clicked_at.strftime("%Y-%m-%d")
        by_date[date_str] = by_date.get(date_str, 0) + 1

        if click.ab_variant in ("A", "B"):
            ab_variants[click.ab_variant] += 1

    return {
        "short_code": short_code,
        "total_clicks": len(clicks),
        "by_country": by_country,
        "by_device": by_device,
        "by_date": by_date,
        "ab_variants": ab_variants,
    }