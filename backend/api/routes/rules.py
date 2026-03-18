from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import get_db
from api.models import Link, Rule
from api.schemas import RuleCreate

router = APIRouter()

VALID_CONDITION_TYPES = {"device", "country", "referrer", "time_range"}
VALID_DEVICES = {"mobile", "desktop", "tablet"}

@router.post("/links/{short_code}/rules")
def add_rule(
    short_code: str,
    payload: RuleCreate,
    token: str,
    db: Session = Depends(get_db)
):
    link = db.query(Link).filter(Link.short_code == short_code).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    if link.manage_token != token:
        raise HTTPException(status_code=403, detail="Invalid manage token")
    if payload.condition_type not in VALID_CONDITION_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"condition_type must be one of {VALID_CONDITION_TYPES}"
        )
    if payload.condition_type == "device" and payload.condition_value.lower() not in VALID_DEVICES:
        raise HTTPException(
            status_code=400,
            detail=f"device must be one of {VALID_DEVICES}"
        )

    rule = Rule(
        link_id=link.id,
        condition_type=payload.condition_type,
        condition_value=payload.condition_value,
        target_url=payload.target_url,
        priority=payload.priority,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return {"id": rule.id, "message": "Rule added successfully"}

@router.delete("/rules/{rule_id}")
def delete_rule(rule_id: int, token: str, db: Session = Depends(get_db)):
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    if rule.link.manage_token != token:
        raise HTTPException(status_code=403, detail="Invalid manage token")
    db.delete(rule)
    db.commit()
    return {"message": "Rule deleted"}

@router.get("/links/{short_code}/rules")
def get_rules(short_code: str, token: str, db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.short_code == short_code).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    if link.manage_token != token:
        raise HTTPException(status_code=403, detail="Invalid manage token")
    return [
        {
            "id": r.id,
            "condition_type": r.condition_type,
            "condition_value": r.condition_value,
            "target_url": r.target_url,
            "priority": r.priority,
        }
        for r in sorted(link.rules, key=lambda r: r.priority)
    ]