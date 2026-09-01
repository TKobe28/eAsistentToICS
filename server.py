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


if __name__ == "__main__":
    import uvicorn
    import json
    from pathlib import Path
    DEFAULT_SERVER_CONFIG_PATH = Path("default_server_config.json")
    SERVER_CONFIG_PATH = Path("server_config.json")

    if not SERVER_CONFIG_PATH.exists():
        logger.info(f"{SERVER_CONFIG_PATH} not found.")
        if not DEFAULT_SERVER_CONFIG_PATH.exists():
            logger.critical(f"{DEFAULT_SERVER_CONFIG_PATH} also not found! Cannot continue.")
            exit()
        logger.info(f"Copying {DEFAULT_SERVER_CONFIG_PATH} to {SERVER_CONFIG_PATH}")
        SERVER_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)  # might not be needed

        cnfg_text = DEFAULT_SERVER_CONFIG_PATH.read_text()
        SERVER_CONFIG_PATH.write_text(cnfg_text)

        server_config = json.loads(cnfg_text)
    else:
        with open(SERVER_CONFIG_PATH, "r") as f:
            server_config = json.load(f)

    uvicorn.run(
        "server:app",
        **server_config
    )
