from models import Config
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from timetable_service import TimetableService


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("init")
    config = Config.load()
    app.state.timetable = TimetableService(config)
    yield
    config.save()
    print("config saving successful")


app = FastAPI(lifespan=lifespan)


@app.get("/calendar/{token}")
async def calendar(token: str):
    service: TimetableService = app.state.timetable

    calendar = await service.get_calendar(token)

    if calendar is None:
        raise HTTPException(404)

    return Response(
        content=calendar,
        media_type="text/calendar",
        headers={
            "Content-Disposition": 'inline; filename="calendar.ics"',
        },
    )
