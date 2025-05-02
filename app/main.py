from fastapi import FastAPI

from routes import task_router

# Main app configuration
app = FastAPI()

# Include the task router
app.include_router(task_router)


