import socks
import socket

from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from src.logger import logger
from src.config import settings
from src.routers import elt_router, excel_router


@asynccontextmanager
async def lifespan(application: FastAPI):
    logger.info("Application is Started")
    if settings.IS_TEST:
        # Setup Socks
        ip, port = 'localhost', 31415
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, ip, port)
        socket.socket = socks.socksocket
    yield
    logger.info("Application is End")

app = FastAPI(
    docs_url='/swagger_docs',
    lifespan=lifespan,
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    summary=settings.APP_SUMMARY,
    description=settings.APP_DESCRIPTION,
)

# Cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(elt_router)
app.include_router(excel_router)
