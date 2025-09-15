from fastapi import FastAPI
from app.api.routers import tasks

app = FastAPI(title="To-Do List API", version="1.0.0")

# include the tasks router (has a /v1 prefix inside)
app.include_router(tasks.router)
