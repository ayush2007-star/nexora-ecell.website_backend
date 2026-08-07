from fastapi.responses import JSONResponse


class ApiResponse:

    @staticmethod
    def success(
        message="Success",
        data=None,
        status_code=200
    ):
        return JSONResponse(
            status_code=status_code,
            content={
                "success": True,
                "message": message,
                "data": data
            }
        )

    @staticmethod
    def error(
        message="Something went wrong",
        errors=None,
        status_code=400
    ):
        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "message": message,
                "errors": errors
            }
        )