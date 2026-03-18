import random

def get_ab_variant(link, ip: str) -> tuple[str, str]:
    bucket = hash(ip) % 100
    if bucket < link.ab_split_ratio:
        return link.default_url, "A"
    return link.ab_url_b, "B"