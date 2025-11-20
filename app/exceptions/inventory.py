from app.exceptions.base import AppError


class InventoryNotFoundError(AppError):
    pass


class InventoryEmptyError(AppError):
    pass


class InventoryAlreadyOwnedError(AppError):
    pass
