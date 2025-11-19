from fastapi import APIRouter

from app.api.handlers import (
    analytics_popular_products,
    life_handler,
    products_purchase,
    products_use,
    users_add_funds,
    users_inventory,
)

api_router = APIRouter()
api_router.include_router(life_handler.router)
api_router.include_router(products_purchase.router)
api_router.include_router(products_use.router)
api_router.include_router(users_inventory.router)
api_router.include_router(users_add_funds.router)
api_router.include_router(analytics_popular_products.router)
