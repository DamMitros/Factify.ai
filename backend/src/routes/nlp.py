from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest

from nlp.pipeline import (predict_proba)

nlp_bp = Blueprint("nlp", __name__)

@nlp_bp.route("/predict", methods=["POST"])
def predict_endpoint():
  payload = request.get_json(silent=True) or {}
  text = str(payload.get("text", "")).strip()
  if not text:
    raise BadRequest("Brak tekstu do analizy.")

  scores = predict_proba(text, return_details=True)
  ai_prob_pct = round(scores["prob_generated"] * 100, 2)
  human_prob_pct = round(scores["prob_human"] * 100, 2)
  response = {
    "text": text,
    "ai_probability": ai_prob_pct,
    "human_probability": human_prob_pct,
    "details": {
      "prob_generated": scores["prob_generated"],
      "prob_generated_std": scores["prob_generated_std"],
      "prob_human": scores["prob_human"],
      "prob_human_std": scores["prob_human_std"],
      "prob_generated_raw": scores["prob_generated_raw"],
      "prob_human_raw": scores["prob_human_raw"],
      "prob_entropy": scores["prob_entropy"],
      "prob_variation_ratio": scores["prob_variation_ratio"],
      "mc_dropout_passes": scores["mc_dropout_passes"],
      "temperature": scores["temperature"],
    },
  }
  if scores["mc_dropout_passes"] > 1:
    response["ai_probability_std"] = round(scores["prob_generated_std"] * 100, 2)
    response["human_probability_std"] = round(scores["prob_human_std"] * 100, 2)
    response["uncertainty_entropy"] = scores["prob_entropy"]
    response["uncertainty_variation_ratio"] = scores["prob_variation_ratio"]

  return jsonify(response)