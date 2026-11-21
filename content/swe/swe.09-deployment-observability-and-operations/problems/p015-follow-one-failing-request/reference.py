import json

ERROR_LEVELS = ("ERROR", "CRITICAL")


def trace_request(lines, request_id):
    events = []
    for line in lines:
        try:
            data = json.loads(line)
        except (TypeError, ValueError):
            continue
        if not isinstance(data, dict) or data.get("request_id") != request_id:
            continue
        events.append({"ts": data.get("ts", ""), "service": data.get("service", "unknown"),
                       "level": data.get("level", ""), "msg": data.get("msg", "")})
    events.sort(key=lambda event: event["ts"])                      # stable: same ts keeps input order
    first_error = next((event for event in events if event["level"] in ERROR_LEVELS), None)
    services = []
    for event in events:
        if event["service"] not in services:
            services.append(event["service"])
    return {"events": events, "first_error": first_error, "services": services}
