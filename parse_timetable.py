import json


def parse_raw(week: str) -> dict:
    week = json.loads(week.splitlines()[1][2:])
    print(week)
    assert week["ok"] is True
    #schedule = week["value"]["schedule"]
    #events = week["value"]["events"]
    return week["value"]
