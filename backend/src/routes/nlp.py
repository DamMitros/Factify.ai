import math

from flask import Blueprint, jsonify, request, current_app
from werkzeug.exceptions import BadRequest, InternalServerError

from nlp.detector.evaluation import predict_proba
from common.python import db
import config
from datetime import datetime

nlp_bp = Blueprint("nlp", __name__)


@nlp_bp.route("/predict", methods=["POST"])
def predict_endpoint():
    payload = request.get_json(silent=True) or {}
    text = str(payload.get("text", "")).strip()
    if not text:
        raise BadRequest("Brak tekstu do analizy.")

    ai_prob = predict_proba(text)
    ai_prob_rounded = round(ai_prob * 100)

    database = db.get_database("factify")
    collection = database["analisys"]
    doc = {
        "text": text,
        "ai_probability": ai_prob_rounded,
        "user_id": "placeholder"
    }
    collection.insert_one(doc)

    return jsonify({
        "text": text,
        "ai_probability": ai_prob_rounded
    })


@nlp_bp.route("/predictions/<user_id>", methods=["GET"])
def get_predictions_by_user(user_id: str):
    user_id = (user_id or "").strip()
    if not user_id:
        raise BadRequest("Missing user_id")

    try:
        database = db.get_database("factify")
        collection = database["analisys"]

        cursor = collection.find({"user_id": user_id}).sort("_id", -1)

        results = [
            {
                "id": str(doc.get("_id")),
                "text": doc.get("text"),
                "ai_probability": doc.get("ai_probability")
            }
            for doc in cursor
        ]

        return jsonify(results)
    except Exception as e:
        current_app.logger.exception("Failed to fetch predictions for user %s: %s", user_id, e)

        raise InternalServerError("Failed to fetch predictions")
