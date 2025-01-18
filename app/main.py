# More info here: https://fastapi.tiangolo.com/tutorial/bigger-applications/#check-the-automatic-api-docs

from fastapi import Depends, FastAPI
from contextlib import asynccontextmanager
import asyncio

from .dependencies import get_query_token, get_token_header
from .internal import admin
from .routers import items, users

# Import your new router and cleanup function
from .routers.chatbot_router import router as chatbot_router, cleanup_inactive_instances

# Store the cleanup task globally so we can cancel it on shutdown
cleanup_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create the background task
    global cleanup_task
    cleanup_task = asyncio.create_task(cleanup_inactive_instances())
    yield
    # Shutdown: cancel the background task
    if cleanup_task:
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass

app = FastAPI(dependencies=[Depends(get_query_token)], lifespan=lifespan)

app.include_router(users.router)
app.include_router(items.router)
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_token_header)],
    responses={418: {"description": "I'm a teapot"}},
)
# Include the chatbot router
app.include_router(chatbot_router, prefix="/chatbot", tags=["Chatbot"])

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}