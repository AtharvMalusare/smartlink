from datetime import datetime, timezone

def evaluate_rules(rules, country: str, device: str, referrer: str) -> str | None:
    sorted_rules = sorted(rules, key=lambda r: r.priority)
    now_time = datetime.now(timezone.utc).strftime("%H:%M")

    for rule in sorted_rules:
        ct = rule.condition_type
        cv = rule.condition_value.lower()

        if ct == "country" and country.lower() == cv:
            return rule.target_url
        elif ct == "device" and device.lower() == cv:
            return rule.target_url
        elif ct == "referrer" and cv in (referrer or "").lower():
            return rule.target_url
        elif ct == "time_range":
            try:
                start, end = cv.split("-")
                if start <= now_time <= end:
                    return rule.target_url
            except Exception:
                pass
    return None