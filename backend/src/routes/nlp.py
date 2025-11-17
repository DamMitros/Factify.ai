from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest

from nlp.detector.evaluation import predict_proba

nlp_bp = Blueprint("nlp", __name__)

@nlp_bp.route("/predict", methods=["POST"])
def predict_endpoint():
  payload = request.get_json(silent=True) or {}
  text = str(payload.get("text", "")).strip()
  if not text:
    raise BadRequest("Brak tekstu do analizy.")

  ai_prob = predict_proba(text)
  return jsonify(
    {
      "text": text,
      "ai_probability": round(ai_prob * 100, 2),
      "human_probability": round((1 - ai_prob) * 100, 2)
    }
  )