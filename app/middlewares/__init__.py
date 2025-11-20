from fastapi import FastAPI

from app.middlewares.error_handler import install_error_middleware


def add_middlewares(app: FastAPI):
    """Add all middleware to the FastAPI application"""

    install_error_middleware(app)
