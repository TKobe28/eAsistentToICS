import json
from models import Week


def parse_raw(week: str) -> dict:
    week = json.loads(week.splitlines()[1][2:])
    print(week)
    assert week["ok"] is True
    #schedule = week["value"]["schedule"]
    #events = week["value"]["events"]
    return week["value"]


def parse_week(week: dict) -> Week:
    for i, event in enumerate(week["events"]):
        if slug := event.get("slug"):
            t, i_ = slug.split("$", 1)
            week["events"][i]["slug_type"] = t
            week["events"][i]["event_id"] = int(i_)

    return Week.model_validate(week)
