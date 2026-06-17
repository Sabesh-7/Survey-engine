from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.core.dependencies import get_embedding_client
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Survey Intelligence Service API",
    )

    @app.on_event("startup")
    async def warm_up_models() -> None:
        await get_embedding_client().warm_up()

    app.include_router(api_router)
    return app


app = create_app()
