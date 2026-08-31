from models import Config
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from timetable_service import TimetableService
from logging_config import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = Config.load()
    app.state.timetable = TimetableService(config)
    logger.debug("Done with initialisation")
    yield
    config.save()
    logger.info("config saved")


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
