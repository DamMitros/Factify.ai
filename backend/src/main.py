from flask import Flask, Blueprint

import config
from routes.example import example_bp
from routes.nlp import nlp_bp

app = Flask(__name__)


def register_route(path: str, blueprint: Blueprint):
    app.register_blueprint(blueprint, url_prefix=config.GLOBAL_PATH_PREFIX + path)


register_route("/example", example_bp)
register_route("/nlp", nlp_bp)

@app.route("/")
def index():
    return "Hello, World!"


if __name__ == "__main__":
    app.run(debug=True, port=8080, host="0.0.0.0")
