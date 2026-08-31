import json
import logging
logger = logging.getLogger(__name__)


def parse_raw(week: str, date: str) -> dict:
    try:
        week_ = week.splitlines()
        week_ = json.loads(week_[1][2:])
        assert week_["ok"] is True
        week_ = week_["value"]
        week_["date"] = date
        return week_
    except Exception as e:
        logger.critical(f"Couldn't parse week ({e}):\n", week)
        raise e
