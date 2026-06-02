from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse


class MESException(HTTPException):
    def __init__(self, status_code: int, code: str, message: str, detail: str = None):
        super().__init__(status_code=status_code)
        self.code = code
        self.message = message
        self.detail = detail


class NotFoundError(MESException):
    def __init__(self, message: str, detail: str = None):
        super().__init__(404, "NOT_FOUND", message, detail)


class ConflictError(MESException):
    def __init__(self, message: str, detail: str = None):
        super().__init__(409, "CONFLICT", message, detail)


class BusinessError(MESException):
    def __init__(self, message: str, detail: str = None):
        super().__init__(422, "BUSINESS_ERROR", message, detail)


class ForbiddenError(MESException):
    def __init__(self, message: str = "접근 권한이 없습니다."):
        super().__init__(403, "FORBIDDEN", message)


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(MESException)
    async def mes_exception_handler(request: Request, exc: MESException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "detail": exc.detail,
                },
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": "HTTP_ERROR",
                    "message": str(exc.detail),
                },
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "서버 오류가 발생했습니다.",
                },
            },
        )
