from fastapi import APIRouter

from app.api.handlers import life_handler, products_purchase, users

api_router = APIRouter()
api_router.include_router(life_handler.router)
api_router.include_router(products_purchase.router)
api_router.include_router(users.router)
