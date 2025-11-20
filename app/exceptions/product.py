from app.exceptions.base import AppError


class ProductNotFoundError(AppError):
    pass


class ProductInactiveError(AppError):
    pass


class ProductNotConsumableError(AppError):
    pass


class ProductNotPermanentError(AppError):
    pass
