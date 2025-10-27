from flask import Flask, Blueprint

import config
from routes import example_bp
from common.python import db

app = Flask(__name__)

db.init_app(app)


def register_route(path: str, blueprint: Blueprint):
    app.register_blueprint(blueprint, url_prefix=config.GLOBAL_PATH_PREFIX + path)


register_route("/example", example_bp)


@app.route("/")
def index():
    return "Hello, World!"


if __name__ == "__main__":
    app.run(debug=True, port=8080, host="0.0.0.0")
