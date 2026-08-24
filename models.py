from pydantic import BaseModel, Field, AliasChoices, AliasPath, model_validator, computed_field, Discriminator
import json
from typing import Optional, Annotated, Literal, ClassVar
from login import AuthSession
from exceptions import ConfigError, InvalidConfig, NoConfigExisting
from functools import cached_property
from datetime import date, time, datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
import ics
from exports import weeks_to_ics
from traceback import format_exception
TIMEZONE = ZoneInfo("Europe/Ljubljana")

"""
navadni tipi:
{'event', 'holiday', 'school_hour'}

slug types:
{
'dogodek',  # normalen dogodek v šoli ALI pa nadomeščanje/odpadla ura/zaposlitev
'ocenjevanje', # isto kot urnik
'osebni_dogodek',  # I love Benjamin Netanyahu  (ima lahko teachers?)
'solski_koledar',  # počitnice ipd.
'urnik'  # navadne šolske ure
}

"""


class Period(BaseModel):
    short_name: str
    name: str
    start_time: time = Field(validation_alias=AliasChoices("start_time", "from"))
    end_time: time = Field(validation_alias=AliasChoices("end_time", "to"))
    is_break: Optional[bool] = None


Schedule = list[Period]


class Event(BaseModel):
    type: str  # {'event', 'holiday', 'school_hour'}
    slug_type: str  # {'dogodek', 'ocenjevanje', 'osebni_dogodek', 'solski_koledar', 'urnik'}
    slug: str
    event_id: int  # not sure what this number means, ig it's just this

    color: str
    title: str
    title_short: str
    description: Optional[str] = None

    # this is in UTC+2 !!!
    date: date
    start_time: time = Field(validation_alias=AliasChoices("start_time", "from"))
    end_time: time = Field(validation_alias=AliasChoices("end_time", "to"))

    schedule_index: list[int]

    type_label: Optional[str] = None
    type_label_short: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def flatten_type_labels(cls, data):
        if labels := data.get("type_labels"):
            first = labels[0]
            data["type_label"] = first.get("type_label")
            data["type_label_short"] = first.get("type_label_short")
        return data

    @computed_field(return_type=datetime)
    @property
    def start_datetime(self) -> datetime:
        """
        start datetime, ADJUSTED TO UTC!
        :return:
        """
        return datetime.combine(
            self.date,
            self.start_time,
            tzinfo=TIMEZONE,
        ).astimezone(timezone.utc)

    @computed_field(return_type=datetime)
    @property
    def end_datetime(self) -> datetime:
        """
        end datetime, ADJUSTED TO UTC!
        :return:
        """
        return datetime.combine(
            self.date,
            self.end_time,
            tzinfo=TIMEZONE,
        ).astimezone(timezone.utc)

    #  if we weren't preprocessing
    #  @model_validator(mode="before")
    #  @classmethod
    #  def parse_slug(cls, data):
    #      if "slug" in data:
    #          t, i = data["slug"].split("$", 1)
    #          data["slug_type"] = t
    #          data["event_id"] = int(i)
    #      return data

    @computed_field
    @property
    def name(self) -> str:
        return self.title

    def get_description(self, schedule: Optional[Schedule] = None) -> str:
        periods = ""
        if len(self.schedule_index) > 1:
            periods = "ure: "
            if schedule:
                periods += ", ".join([period.short_name for i, period in enumerate(schedule) if i in self.schedule_index])
            else:
                periods += ", ".join([f"{period}." for period in self.schedule_index])
        elif len(self.schedule_index) == 1:
            periods = "ura: " + schedule[self.schedule_index[0]].short_name if schedule else self.schedule_index[0]

        return periods + (f"\n{self.description}" if self.description is not None else "")

    def get_other_ics_arguments(self) -> dict:
        return dict()

    def to_ics(self, schedule: Optional[Schedule] = None) -> ics.Event:
        return ics.Event(
            name=self.name,
            description=self.get_description(schedule),
            uid=str(self.event_id),
            begin=self.start_datetime,
            end=self.end_datetime,
            classification=self.slug_type,
            **self.get_other_ics_arguments()
        )


class Holiday(Event):
    type: Literal["holiday"]


class PersonalEvent(Event):
    type: Literal["event"]
    slug_type: Literal["osebni_dogodek"]


class SchoolEvent(Event):
    type: Literal["event"]
    slug_type: Literal["dogodek"]
    teachers: Optional[list[str]] = None
    classroom: Optional[str] = None

    def get_other_ics_arguments(self) -> dict:
        other_ics_arguments = dict()
        if self.teachers is not None:
            other_ics_arguments["organizer"] = ", ".join(self.teachers)
        if self.classroom is not None:
            other_ics_arguments["location"] = self.classroom
        return other_ics_arguments


class Subject(BaseModel):
    subject_id: int
    title: str
    title_short: str
    color: str


class Evaluation(BaseModel):
    title: str
    evaluation_id: int
    grade_color: str
    grade_type: str
    summary: str


class Homework(BaseModel):
    title: str
    due_date: date
    summary: str


class SchoolHour(Event):
    type: Literal["school_hour"]
    slug_type: Literal["urnik", "ocenjevanje"]

    teachers: list[str]
    classroom: str
    subject: Subject

    evaluation: Optional[Evaluation] = None
    homework: Optional[list[Homework]] = None

    def get_other_ics_arguments(self) -> dict:
        return {
            "location": self.classroom
        }


class SpecialSchoolHour(SchoolHour):
    type: Literal["event"]

    type_label: str = "POSEBNOST"
    type_label_short: str = "?"

    classroom: Optional[str] = None
    subject: Optional[Subject] = None
    original_subject: Optional[str] = None

    @computed_field
    @property
    def name(self) -> str:
        return f"[{self.type_label_short}] {super().name}"

    def get_description(self, schedule: Optional[Schedule] = None) -> str:
        return self.type_label + "\n" + super().get_description(schedule)


# this would be hard to implement because type_label is made later and there is no good reason
# class SubSchoolHour(SpecialSchoolHour):
#     type_label: Literal["NADOMEŠČANJE"]
#
#
# class CancelledSchoolHour(SpecialSchoolHour):
#     type_label: Literal["ODPADLA URA"]
#
#
# class AssignmentSchoolHour(SpecialSchoolHour):
#     type_label: Literal["ZAPOSLITEV"]
#
#  AnySpecialSchoolHour = Annotated[
#      SpecialSchoolHour |
#      SubSchoolHour |
#      CancelledSchoolHour |
#      AssignmentSchoolHour,
#      Discriminator(??)
#  ]

# uwu
AnyEvent = Annotated[
    Holiday | Annotated[
        PersonalEvent | SchoolEvent | Annotated[
            SchoolHour | SpecialSchoolHour, Field(discriminator="type")
        ],
        Field(discriminator="slug_type")
    ],
    Field(discriminator="type")
]


class Week(BaseModel):
    date: date
    schedule: Schedule
    events: list[AnyEvent]
    unpublished_schedule_message: str | None = None

    @classmethod
    def model_validate(cls, week: dict, *, strict = None, extra = None, from_attributes = None, context = None, by_alias = None, by_name = None):
        for i, event in enumerate(week["events"]):
            if slug := event.get("slug"):
                t, i_ = slug.split("$", 1)
                week["events"][i]["slug_type"] = t
                week["events"][i]["event_id"] = int(i_)
        return super().model_validate(week, strict=strict, extra=extra, from_attributes=from_attributes, context=context, by_alias=by_alias, by_name=by_name)


class UserConfig(BaseModel):
    username: str
    password: str
    min_update_time: timedelta = timedelta(seconds=15)
    calendar_token: str
    last_update: datetime = datetime.fromtimestamp(0)

    def __repr__(self):
        return f'Uporabnik({self.username}, ****, {self.calendar_token})'


class User(UserConfig):
    _auth: AuthSession | None = None

    weeks: list[Week] = list()
    _calendar: ics.Calendar | None = None
    _calendar_str: str | None = None

    async def update_calendar(self, start_date: date | None = None, max_date: date = None, cache_path: str = "./cache/", hard: bool = False) -> ics.Calendar:
        """
        :param start_date: The start of the period. If left None, the period will start with last 1st september.
        :param max_date: not implemented - todo
        :param hard: if we discard cache. If False only weeks in the present or future will be updated.
        :return:
        """
        now = datetime.now()
        if now - self.last_update < self.min_update_time:
            if self._calendar is None:
                self._calendar = weeks_to_ics(self.weeks)
            return self._calendar

        if start_date is None:
            first_september = date(now.year if now.month > 8 else now.year-1, 9, 1)
            start_date = first_september if hard else max(first_september, self.last_update.date())

        print(f"updating calendar, start_date is {start_date}.")
        for i, week in enumerate(self.weeks):
            if week.date >= start_date:
                self.weeks = self.weeks[:i]
                break

        current = start_date - timedelta(days=start_date.weekday())  # Monday

        new_weeks = []
        unpublished = False
        while not unpublished:
            new_weeks.append(await self.auth_session.get_week(str(current)))
            current += timedelta(weeks=1)
            unpublished = new_weeks[-1].unpublished_schedule_message is not None

        if hard:
            self.weeks = new_weeks
        else:
            self.weeks += new_weeks

        self._calendar = weeks_to_ics(self.weeks)
        self.last_update = now
        self._calendar_str = None
        return self._calendar        

    async def get_calendar(self, start_date: datetime | None = None,  max_weeks_in_future: int = 10, cache_path: str = "./cache/") -> str:
        if self._calendar is None:
            await self.update_calendar(start_date, max_weeks_in_future, cache_path)
        if self._calendar_str is None:
            self._calendar_str = self._calendar.serialize()
        return self._calendar_str
    
    @property
    def auth_session(self) -> AuthSession:
        if not self._auth:
            self._auth = AuthSession(self.username, self.password)
        return self._auth


class Config(BaseModel):
    user_configs: list[UserConfig]
    cache_path: str = "./cache/"

    token_length: int = 32

    @cached_property
    def users(self) -> list[User]:
        result = []
        for uc in self.user_configs:
            weeks = self._load_weeks(uc.username)
            result.append(User(**uc.model_dump(), weeks=weeks))
        return result

    def _load_weeks(self, username: str) -> list[Week]:
        path = Path(self.cache_path + f"{username}.json")
        if not path.exists():
            return []
        return [Week.model_validate(w) for w in json.loads(path.read_text())]

    @classmethod
    def load(cls, config_path: Path = Path("./config.json")):
        if config_path.exists():
            try:
                with open(config_path) as f:
                    return cls.model_validate_json(f.read())
            except Exception as e:
                raise InvalidConfig(str(e))
        else:
            raise NoConfigExisting()

    def save_user_cache(self, user: User):
        path = Path(self.cache_path + f"{user.username}.json")
        path.write_text(json.dumps([w.model_dump(mode="json") for w in user.weeks]))

    def save_users_cache(self):
        for user in self.users:
            try:
                self.save_user_cache(user)
            except Exception as e:
                print(f"OOPSIE!! {e} when saving {user.username}s cache! Error: ", '\n'.join(format_exception(e)))

    def save(self, config_path: Path = Path("./config.json")):
        self.save_users_cache()
        with open(config_path, "w") as f:
            f.write(self.model_dump_json(indent=2))

