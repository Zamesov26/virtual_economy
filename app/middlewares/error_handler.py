import asyncio
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions.base import AppError
from app.exceptions.inventory import (
    InventoryAlreadyOwnedError,
    InventoryNotFoundError,
    InventoryEmptyError,
)
from app.exceptions.product import (
    ProductInactiveError,
    ProductNotConsumableError,
    ProductNotFoundError,
    ProductNotPermanentError,
)
from app.exceptions.user import UserLowBalanceError, UserNotFoundError, UserInvalidTopUpAmountError, \
    UserIdempotencyConflictError

logger = logging.getLogger(__name__)

SYSTEM_EXCEPTIONS = (
    KeyboardInterrupt,
    SystemExit,
    asyncio.CancelledError,
)

ERROR_MAP = {
    # user
    UserNotFoundError: (404, "User not found"),
    UserLowBalanceError: (409, "Not enough funds"),
    UserInvalidTopUpAmountError: (400, "Amount must be greater than zero"),
    UserIdempotencyConflictError: (409, "Duplicate top-up request"),
    # product
    ProductNotFoundError: (404, "Product not found"),
    ProductInactiveError: (400, "Product is inactive"),
    ProductNotConsumableError: (400, "Product is not consumable"),
    ProductNotPermanentError: (400, "Product is not permanent"),
    # inventory
    InventoryNotFoundError: (400, "Item not found in inventory"),
    InventoryEmptyError: (400, "Item quantity is zero"),
    InventoryAlreadyOwnedError: (409, "Permanent product already owned"),
}


def install_error_middleware(app: FastAPI):
    @app.middleware("http")
    async def error_middleware(request: Request, call_next):
        try:
            return await call_next(request)

        except AppError as exc:
            for exc_type, (status, detail) in ERROR_MAP.items():
                if isinstance(exc, exc_type):
                    return JSONResponse(
                        status_code=status,
                        content={
                            "error": {"type": exc_type.__name__, "message": detail}
                        },
                    )

            return JSONResponse(
                status_code=400,
                content={
                    "error": {"type": exc.__class__.__name__, "message": str(exc)}
                },
            )
        except SYSTEM_EXCEPTIONS:
            raise  # не подавлять системные сигналы

        except Exception:
            logger.exception("Unexpected server error")

            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "type": "InternalServerError",
                        "message": "Internal server error",
                    }
                },
            )
