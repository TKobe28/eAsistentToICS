from pydantic import BaseModel, Field, AliasChoices, AliasPath, model_validator, computed_field, Discriminator
from typing import Optional, Annotated, Literal
# todo: from functools import cached_property
from datetime import date, time, datetime, timezone
from zoneinfo import ZoneInfo
import ics

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
    schedule: Schedule
    events: list[AnyEvent]
