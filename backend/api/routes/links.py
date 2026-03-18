from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import get_db
from api.models import Link
from api.schemas import LinkCreate, LinkResponse
from api.services.shortcode import generate_short_code, is_valid_slug
import uuid

router = APIRouter()

BASE_URL = "http://localhost:8000"

@router.post("/links", response_model=LinkResponse)
def create_link(payload: LinkCreate, db: Session = Depends(get_db)):
    if payload.custom_slug:
        valid, error = is_valid_slug(payload.custom_slug)
        if not valid:
            raise HTTPException(status_code=400, detail=error)
        
        existing = db.query(Link).filter(Link.short_code == payload.custom_slug).first()
        if existing:
            raise HTTPException(status_code=409, detail="Slug already taken")
        short_code = payload.custom_slug
    else:
        for _ in range(5):
            code = generate_short_code()
            if not db.query(Link).filter(Link.short_code == code).first():
                short_code = code
                break
        else:
            raise HTTPException(status_code=500, detail="Could not generate unique code")

    link = Link(
        short_code=short_code,
        default_url=payload.default_url,
        manage_token=str(uuid.uuid4()),
        expires_at=payload.expires_at,
        is_ab_test=payload.is_ab_test,
        ab_url_b=payload.ab_url_b,
        ab_split_ratio=payload.ab_split_ratio,
    )
    db.add(link)
    db.commit()
    db.refresh(link)

    return LinkResponse(
        short_code=link.short_code,
        short_url=f"{BASE_URL}/{link.short_code}",
        default_url=link.default_url,
        manage_token=link.manage_token,
        created_at=link.created_at,
        expires_at=link.expires_at,
        warning="Save your manage_token — it's the only way to edit or delete this link"
    )

@router.put("/links/{short_code}")
def update_link(
    short_code: str,
    payload: LinkCreate,
    token: str,
    db: Session = Depends(get_db)
):
    link = db.query(Link).filter(Link.short_code == short_code).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
        
    if link.manage_token != token:
        raise HTTPException(status_code=403, detail="Invalid manage token")
        
    link.default_url = payload.default_url
    link.expires_at = payload.expires_at
    link.is_ab_test = payload.is_ab_test
    link.ab_url_b = payload.ab_url_b
    link.ab_split_ratio = payload.ab_split_ratio
    
    db.commit()
    
    from api.services.cache import invalidate_link
    invalidate_link(short_code)
    
    return {"message": "Link updated"}

@router.delete("/links/{short_code}")
def delete_link(short_code: str, token: str, db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.short_code == short_code).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
        
    if link.manage_token != token:
        raise HTTPException(status_code=403, detail="Invalid manage token")
        
    db.delete(link)
    db.commit()
    
    from api.services.cache import invalidate_link
    invalidate_link(short_code)
    
    return {"message": "Link deleted"}