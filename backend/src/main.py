from flask import Flask, Blueprint
from flask_cors import CORS
import config
from routes.example import example_bp

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "http://frontend:3000"}})

def register_route(path: str, blueprint: Blueprint):
    app.register_blueprint(blueprint, url_prefix=config.GLOBAL_PATH_PREFIX + path)


register_route("/example", example_bp)


@app.route("/")
def index():
    return "Hello, World!"



if __name__ == "__main__":
    app.run(debug=True, port=8080, host="0.0.0.0")
