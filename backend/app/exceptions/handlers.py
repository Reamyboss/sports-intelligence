import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Catch-all for anything that isn't an HTTPException or a request
    validation error (both of which FastAPI already turns into clean
    JSON on its own). Without this, an unexpected bug - like a
    pydantic ValidationError raised inside business logic - falls
    through to Starlette's default handler, which returns plain text
    instead of the {"detail": ...} JSON shape every other error on
    this API uses.
    """

    logger.exception(
        "Unhandled error on %s %s",
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error."},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(Exception, unhandled_exception_handler)
