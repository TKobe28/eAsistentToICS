from models import User, Config, ics


class TimetableService:
    def __init__(self, config: Config):
        self.config = config
        config.users

    async def get_calendar(self, token: str) -> (str | None):
        for user in self.config.users:  # todo!!
            if user.calendar_token == token:
                return await user.get_calendar()
        return None
