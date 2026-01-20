from flask import Flask, Blueprint
from flask_cors import CORS

from nlp.detector.model_utils import load_model_artifacts
from routes import example_bp, nlp_bp, user_bp, image_bp
from common.python import db

import config

app = Flask(__name__)

db.init_app(app)

CORS(app, resources={r"/*": {"origins": ["http://frontend:3000", "http://localhost:3000"]}})

# USUŃ TĘ LINIĘ - to FastAPI, nie Flask!
# app.include_router(image_detection_router)


def register_route(path: str, blueprint: Blueprint):
    app.register_blueprint(blueprint, url_prefix=config.GLOBAL_PATH_PREFIX + path)


register_route("/example", example_bp)
register_route("/nlp", nlp_bp)
register_route("/user", user_bp)
register_route("/image", image_bp)  


@app.route("/")
def index():
    return "Hello, World!"

print("Loading NLP model artifacts...")
try:
    load_model_artifacts()
    print("NLP model artifacts loaded successfully.")
except Exception as e:
    print(f"Error loading NLP model artifacts: {e}")
    
if __name__ == "__main__":
    app.run(debug=True, port=8080, host="0.0.0.0")