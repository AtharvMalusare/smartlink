from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.database import get_db
from api.models import Link
from api.services.shortcode import is_valid_slug

router = APIRouter()

@router.get("/check/{slug}")
def check_slug(slug: str, db: Session = Depends(get_db)):
    valid, error = is_valid_slug(slug)
    if not valid:
        return {"available": False, "reason": error}
    exists = db.query(Link).filter(Link.short_code == slug).first()
    if exists:
        return {"available": False, "reason": "Already taken"}
    return {"available": True}