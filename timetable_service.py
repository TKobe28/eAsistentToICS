from models import User, Config, ics


class TimetableService:
    def __init__(self, config: Config):
        self.config = config

    async def get_calendar(self, token: str) -> (ics.Calendar | None):
        for user in self.config.users: # todo!!
            if user.calendar_token == token:
                return await user.get_calendar()
        return None
    