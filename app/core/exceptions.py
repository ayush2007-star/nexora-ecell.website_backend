from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation Error",
            "errors": exc.errors(),
        },
    )