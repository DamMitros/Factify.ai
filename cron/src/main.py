import sys
import time
import os
import traceback
from datetime import datetime, timezone
from typing import Any
import importlib

from pymongo import ReturnDocument
from pymongo.collection import Collection

from common.python import db
from context import TaskContext

DB_NAME = os.getenv("MONGODB_DB", "factify")
TASKS_COLLECTION = "cron_tasks"
POLL_INTERVAL_SEC = float(os.getenv("CRON_POLL_INTERVAL_SEC", "2"))

handlers_cache = {}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def ensure_indexes(col: Collection) -> None:
    col.create_index([("createdAt", 1)])
    col.create_index([("status", 1)])
    col.create_index([("name", 1)], unique=False)


def claim_due_task(col: Collection) -> dict[str, Any] | None:
    now = utcnow()

    query = {"status": "scheduled"}

    update = {
        "$set": {"status": "in_progress", "startedAt": now},
    }

    return col.find_one_and_update(
        query,
        update,
        sort=[("createdAt", 1)],
        return_document=ReturnDocument.AFTER,
    )


def get_handler_module(name: str):
    global handlers_cache

    if name in handlers_cache:
        return handlers_cache[name]
    else:
        mod = importlib.import_module(f"jobs.{name}")
        handlers_cache[name] = mod
        return mod


def process_task(col: Collection, task: dict[str, Any], ctx: TaskContext) -> None:
    name = task.get("name")
    payload = task.get("payload")
    now = utcnow()

    try:
        handler_mod = get_handler_module(name)
    except ImportError:
        print(traceback.format_exc(), file=sys.stderr)
        handler_mod = None

    handler_fn = handler_mod.task if handler_mod else None
    error_info = None

    if handler_fn is None:
        error_info = f"No handler for task '{name}'"
    else:
        try:
            handler_fn(payload, ctx)
        except Exception:
            error_info = traceback.format_exc()

    update = {
        "$set": {
            "lastRunAt": now,
            "completedAt": now,
            "status": "error" if error_info else "success",
        },
    }

    if error_info:
        update["$set"]["lastError"] = error_info

    col.update_one({"_id": task["_id"]}, update)


def loop(col: Collection) -> None:
    processed_any = False

    ctx = TaskContext()
    ctx.db = db.get_client()

    while True:
        task = claim_due_task(col)

        if not task:
            break

        processed_any = True
        print(f"⚙️  Processing task: {task.get('name')} (id={task.get('_id')})")
        process_task(col, task, ctx)

    if not processed_any:
        print("⏳ Waiting for tasks...")


if __name__ == "__main__":
    db.init_standalone()

    database = db.get_database(DB_NAME)
    tasks = database[TASKS_COLLECTION]
    ensure_indexes(tasks)

    while True:
        loop(tasks)
        time.sleep(POLL_INTERVAL_SEC)
