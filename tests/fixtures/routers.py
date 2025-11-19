import pytest

from tests.rate_limit_router import test_router


@pytest.fixture(scope="module", autouse=True)
def register_test_router():
    from app.main import app

    app.include_router(test_router, prefix="/api/v1")
    yield
