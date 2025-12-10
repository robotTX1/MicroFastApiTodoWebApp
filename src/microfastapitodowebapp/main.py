from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from loguru import logger
from starsessions import SessionMiddleware, SessionAutoloadMiddleware

from microfastapitodowebapp.config import logging
from microfastapitodowebapp.config.middleware import AuthGuardMiddleware, RequestContextMiddleware, \
    HTMXRedirectMiddleware
from microfastapitodowebapp.config.valkey import valkey_store, valkey_client
from microfastapitodowebapp.router import landing, dashboard, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    logger.info("Application shutting down, closing Valkey client...")
    await valkey_client.aclose()
    logger.info("Valkey client closed.")

app = FastAPI(lifespan=lifespan)
# Config
logging.setup_logging()
app.mount("/static", StaticFiles(directory="src/resources/static"), name="static")

# Middleware
app.add_middleware(RequestContextMiddleware)
app.add_middleware(AuthGuardMiddleware, callback_endpoint_name="auth_callback",
                   public_urls=["/", "/favicon.ico", "/login**", "/static/**"])
app.add_middleware(HTMXRedirectMiddleware)
app.add_middleware(SessionAutoloadMiddleware)
app.add_middleware(SessionMiddleware, store=valkey_store, lifetime=3600, rolling=True)

# Routers
app.include_router(landing.router)
app.include_router(dashboard.router)
app.include_router(auth.router)

