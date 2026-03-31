from flask import Flask, Blueprint
from flask_cors import CORS

from routes import example_bp, user_bp, admin_bp, social_bp, image_bp, manipulation_bp, find_sources_bp, ai_text_bp
from common.python import db

import config

app = Flask(__name__)

db.init_app(app)

CORS(app, resources={r"/*": {"origins": ["http://frontend:3000", "http://localhost:3000"]}})


def register_route(path: str, blueprint: Blueprint):
    app.register_blueprint(blueprint, url_prefix=config.GLOBAL_PATH_PREFIX + path)


register_route("/example", example_bp)
register_route("/user", user_bp)
register_route("/image", image_bp)  
register_route("/analysis/manipulation", manipulation_bp)
register_route("/analysis/find_sources", find_sources_bp)
register_route("/analysis/ai", ai_text_bp)
register_route("/admin", admin_bp)
register_route("/social", social_bp)

@app.route("/")
def index():
    return "Hello, World!"
    
if __name__ == "__main__":
    app.run(debug=True, port=8080, host="0.0.0.0")