from fastapi import FastAPI
from app.api.routers import tasks

app = FastAPI(
    title="To-Do List API",
    version="1.0.0"
)

#just tasks for now
app.include_router(tasks.router)
