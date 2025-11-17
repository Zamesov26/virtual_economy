from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.handlers.routers_v1 import api_router as v1_routers
from app.middlewares import add_middlewares
from app.settings import Settings

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.engine = create_async_engine(settings.db.url)
    app.state.session_maker = async_sessionmaker(
        app.state.engine, expire_on_commit=False
    )
    yield
    await app.state.engine.dispose()


app = FastAPI(
    title=settings.api.name,
    version=settings.api.version,
    debug=settings.api.debug,
    lifespan=lifespan,
)

add_middlewares(app)
app.include_router(v1_routers, prefix="/api/v1")
