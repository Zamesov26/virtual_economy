from app.exceptions.base import AppError


class UserNotFoundError(AppError):
    pass


class UserLowBalanceError(AppError):
    pass

class UserInvalidTopUpAmountError(AppError):
    """Пополнение на некорректную сумму."""
    pass

class UserIdempotencyConflictError(AppError):
    """Повторный запрос по тому же idempotency-key."""
    pass