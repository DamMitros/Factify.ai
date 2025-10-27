from flask import Blueprint

import common.python.db as db

example_bp = Blueprint("example", __name__)


@example_bp.route("/hello", methods=["GET"])
def hello():
    db.get_database("test_database").create_collection("test_collection")

    return "Hello, World!", 200
