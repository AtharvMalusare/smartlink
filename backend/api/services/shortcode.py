import random
import string
import re

CHARS = string.ascii_letters + string.digits
RESERVED = {"api", "admin", "health", "static", "docs", "redoc"}

def generate_short_code(length=6):
    return ''.join(random.choices(CHARS, k=length))

def is_valid_slug(slug: str) -> tuple[bool, str]:
    if len(slug) < 3:
        return False, "Slug must be at least 3 characters"
    if len(slug) > 50:
        return False, "Slug must be under 50 characters"
    if not re.match(r'^[a-zA-Z0-9-]+$', slug):
        return False, "Only letters, numbers, and hyphens allowed"
    if slug in RESERVED:
        return False, "This slug is reserved"
    return True, ""