import json
import os.path
from datetime import date, timedelta
from pathlib import Path
import parse_timetable
from models import Week
from login import AuthSession
from config import get_config

def get_week(auth_session: AuthSession, _date: str, folder="./cache/", rewrite: bool = False, verbose: bool = False) -> Week:
    path = Path(folder + auth_session.username + "/" + _date + ".json")
    path.parent.mkdir(parents=True, exist_ok=True)
    if rewrite is False and os.path.exists(path):
        if verbose:
            print("Week already exists. Not rewriting")
        try:
            with open(path, "r") as f:
                return parse_timetable.parse_week(json.load(f))
        except Exception as e:
            print(f"Error while opening cached week {path}, attempting refetching and rewriting. Error was:", e)

    week = auth_session.fetch_week(_date, verbose=verbose)
    with open(path, "w") as f:
        json.dump(week, f, indent=2)

    return parse_timetable.parse_week(week)


def get_weeks(auth_session: AuthSession, start: date, end: date, folder="./cache/", rewrite: bool = False, verbose: bool = False) -> list[Week]:
    current = start - timedelta(days=start.weekday())  # Monday
    weeks = []
    while current <= end:
        if verbose:
            print("getting week", current)
        weeks.append(get_week(auth_session=auth_session, _date=str(current), folder=folder, rewrite=rewrite, verbose=verbose))
        current += timedelta(weeks=1)

    return weeks


if __name__ == "__main__":
    config = get_config()
    auth_session = AuthSession(config.users[0].username, config.users[0].password, login=False)
    get_weeks(auth_session=auth_session, start=date(2025, 9, 1), end=date(2026, 6, 20), rewrite=False)
