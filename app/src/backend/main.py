from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, generate_latest
from prometheus_client.openmetrics.exposition import (
    CONTENT_TYPE_LATEST as OPENMETRICS_CONTENT_TYPE,
    generate_latest as generate_openmetrics_latest
)
from slowapi.middleware import SlowAPIMiddleware
from starlette.requests import Request

from configuration.app_init import init
from configuration.database import async_engine
from configuration.metrics_middleware import MetricsMiddleware
from configuration.rate_limit import limiter
from configuration.telemetry import configure_tracing, instrument_app
from exception.global_exception_handler import add_exception_handlers
from router import auth_router, student_router, user_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init()
    yield
    await async_engine.dispose()


configure_tracing()

app = FastAPI(lifespan=lifespan)

instrument_app(app)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(MetricsMiddleware)

add_exception_handlers(app)


@app.get('/', tags=['Root'])
@limiter.limit('10/minute')
async def root(request: Request):
    return {'message': 'Hello Viettel Digital Talent 2026!!!!!'}


@app.get('/metrics', tags=['Metrics'])
async def metrics(request: Request):
    accept = request.headers.get('accept', '')

    if 'application/openmetrics-text' in accept:
        return Response(
            content=generate_openmetrics_latest(REGISTRY),
            media_type=OPENMETRICS_CONTENT_TYPE
        )
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


app.include_router(auth_router.router)
app.include_router(student_router.router)
app.include_router(user_router.router)
