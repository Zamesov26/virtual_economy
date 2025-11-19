from fastapi import APIRouter, Depends

from app.utils.rate_limiter import simple_rate_limit

test_router = APIRouter()


@test_router.get("/test-rate")
async def rate_limit_handler(_rl=Depends(simple_rate_limit(3, 60))):
    return {"ok": True}
