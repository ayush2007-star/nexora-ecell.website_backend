from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


class ApiResponse:
    """
    Centralized API response formatter.

    jsonable_encoder is important because MongoDB responses can
    contain datetime/ObjectId values that JSONResponse cannot
    serialize directly.
    """

    @staticmethod
    def success(
        message: str = "Success",
        data: Any = None,
        status_code: int = 200,
    ):
        return JSONResponse(
            status_code=status_code,
            content=jsonable_encoder(
                {
                    "success": True,
                    "message": message,
                    "data": data,
                }
            ),
        )

    @staticmethod
    def error(
        message: str = "Something went wrong",
        errors: Any = None,
        status_code: int = 400,
    ):
        return JSONResponse(
            status_code=status_code,
            content=jsonable_encoder(
                {
                    "success": False,
                    "message": message,
                    "errors": errors,
                }
            ),
        )