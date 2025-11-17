from __future__ import annotations

from flask import Flask, current_app
from pymongo import MongoClient

import config

_client: MongoClient | None = None


def _build_mongo_uri() -> str:
    user = config.MONGODB_USER
    password = config.MONGODB_PASSWORD
    host = config.MONGODB_HOST
    port = config.MONGODB_PORT

    return f"mongodb://{user}:{password}@{host}:{port}"


def init_app(app: Flask) -> None:
    global _client

    if _client is None:
        uri = _build_mongo_uri()
        _client = MongoClient(uri)

    app.extensions = getattr(app, "extensions", {})
    app.extensions["mongo_client"] = _client


def get_client() -> MongoClient:
    global _client

    if _client is not None:
        return _client

    app_client = current_app.extensions.get("mongo_client")

    if app_client is not None:
        return app_client

    raise Exception("Mongo client not initialized. init_app() wasn't called first?")


def get_database(name: str | None = None):
    return get_client()[name]
