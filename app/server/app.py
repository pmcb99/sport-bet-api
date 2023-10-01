import logging

from fastapi import FastAPI
import redis

from app.server.database import engine
from app.server.models import models
from fastapi import FastAPI

from app.server.routers import sport, sports, event, events, selection, selections

from app.server.redis import redis_client

logger = logging.getLogger(
    __name__
)  # the __name__ resolve to "main" since we are at the root of the project.
# This will get the root logger since no logger in the configuration has this name.

app = FastAPI()

app.include_router(sport.router)
app.include_router(sports.router)

app.include_router(event.router)
app.include_router(events.router)


app.include_router(selection.router)
app.include_router(selections.router)

models.Base.metadata.create_all(bind=engine)

@app.on_event("shutdown")
async def shutdown_event():
    redis_client.close()

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}