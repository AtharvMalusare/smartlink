from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from api.database import Base
import uuid

class Link(Base):
    __tablename__ = "links"

    id             = Column(Integer, primary_key=True, index=True)
    short_code     = Column(String(50), unique=True, nullable=False, index=True)
    default_url    = Column(Text, nullable=False)
    manage_token   = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    created_at     = Column(DateTime, default=datetime.utcnow)
    expires_at     = Column(DateTime, nullable=True)
    is_ab_test     = Column(Boolean, default=False)
    ab_url_b       = Column(Text, nullable=True)
    ab_split_ratio = Column(Integer, default=50)

    rules  = relationship("Rule", back_populates="link", cascade="all, delete")
    clicks = relationship("Click", back_populates="link", cascade="all, delete")


class Rule(Base):
    __tablename__ = "rules"

    id              = Column(Integer, primary_key=True, index=True)
    link_id         = Column(Integer, ForeignKey("links.id"), nullable=False)
    condition_type  = Column(String(20), nullable=False)
    condition_value = Column(String(100), nullable=False)
    target_url      = Column(Text, nullable=False)
    priority        = Column(Integer, default=0)

    link = relationship("Link", back_populates="rules")


class Click(Base):
    __tablename__ = "clicks"

    id              = Column(Integer, primary_key=True, index=True)
    link_id         = Column(Integer, ForeignKey("links.id"), nullable=False)
    clicked_at      = Column(DateTime, default=datetime.utcnow)
    country         = Column(String(2), nullable=True)
    device          = Column(String(10), nullable=True)
    referrer        = Column(Text, nullable=True)
    matched_rule_id = Column(Integer, nullable=True)
    ab_variant      = Column(String(1), nullable=True)

    link = relationship("Link", back_populates="clicks")