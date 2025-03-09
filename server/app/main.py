import uvicorn
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import LOGGING_CONFIG
from app.health import api_router as health_router
from app.api.v1.route import api_router as api_v1_router
from app.preload import settings

logger = logging.getLogger("uvicorn")


app = FastAPI(
    debug=settings.debug,
    title=settings.title,
    description=settings.description,
    version=settings.version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(api_v1_router)


def main():
    uvicorn.run(
        "main:app", host="0.0.0.0", port=settings.port, log_config=LOGGING_CONFIG
    )


if __name__ == "__main__":
    main()
