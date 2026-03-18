from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class LinkCreate(BaseModel):
    default_url: str
    custom_slug: Optional[str] = None
    expires_at: Optional[datetime] = None
    is_ab_test: bool = False
    ab_url_b: Optional[str] = None
    ab_split_ratio: int = 50

class LinkResponse(BaseModel):
    short_code: str
    short_url: str
    default_url: str
    manage_token: str
    created_at: datetime
    expires_at: Optional[datetime]
    warning: str = "Save your manage_token — it's the only way to edit or delete this link"

    class Config:
        from_attributes = True

class RuleCreate(BaseModel):
    condition_type: str
    condition_value: str
    target_url: str
    priority: int = 0

class AnalyticsResponse(BaseModel):
    total_clicks: int
    by_country: dict
    by_device: dict
    by_date: dict
    ab_variants: dict