from datetime import date
from ics import Calendar
from collections import defaultdict
from models import *
from login import AuthSession


def weeks_to_ics(weeks: list["Week"]) -> Calendar:
    calendar = Calendar()

    #  num_of_instances = defaultdict(int)
    for week in weeks:
        for event in week.events:
            #  num_of_instances[event.__class__.__name__] += 1
            calendar.events.add(
                event.to_ics(week.schedule)
            )
    #  print(dict(num_of_instances))

    return calendar


if __name__ == "__main__":
    from getter import get_weeks
    from config import get_config
    config = get_config()
    auth_session = AuthSession(config.users[0].username, config.users[0].password, login=False)
    weeks = get_weeks(auth_session=auth_session, start=date(2025, 9, 1), end=date(2026, 6, 20), rewrite=False)
    calendar = weeks_to_ics(weeks)
    output = "calendar.ics"
    with open(output, "w") as f:
        f.writelines(calendar)
