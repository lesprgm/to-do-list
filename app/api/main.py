from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import tasks  # adjust import if your router file name differs

# Create FastAPI app
app = FastAPI(
    title="To-Do List API",
    version="1.0.0"
)

# Enable CORS (important for frontend connection)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can replace with ["http://localhost:3000"] for stricter
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tasks.router, prefix="/v1/tasks", tags=["tasks"])

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "To-Do API is running 🚀"}
