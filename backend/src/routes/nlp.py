import json
from flask import Blueprint, jsonify, request, current_app
from werkzeug.exceptions import BadRequest, InternalServerError

from nlp import predict_proba, predict_segmented_text
from nlp.detector.config import SEGMENT_MIN_WORDS, SEGMENT_STRIDE_WORDS, SEGMENT_WORD_TARGET
from common.python import db
from common.python.text_extractor import extract_text

nlp_bp = Blueprint("nlp", __name__)

def helper_to_predict(text, detailed_raw, segment_params_raw):
  if not text:
    raise BadRequest("No text provided for analysis.")
   
  wants_segments = True
  if detailed_raw is not None:
    if isinstance(detailed_raw, str):
      wants_segments = detailed_raw.strip().lower() not in {"false", "0"}
    else:
      wants_segments = bool(detailed_raw)

  segment_params = segment_params_raw
  if isinstance(segment_params, str):
    try:
      segment_params = json.loads(segment_params)
    except:
      segment_params = {}
  segment_params = segment_params or {}
  if wants_segments:
    words_per_chunk = int(segment_params.get("words_per_chunk", SEGMENT_WORD_TARGET))
    stride_words = segment_params.get("stride_words", SEGMENT_STRIDE_WORDS)
    if stride_words is not None:
      stride_words = int(stride_words)
    min_words = int(segment_params.get("min_words", SEGMENT_MIN_WORDS))
    max_length = int(segment_params.get("max_length", 128))

    segmented = predict_segmented_text(
      text,
      words_per_chunk=words_per_chunk,
      stride_words=stride_words,
      min_words=min_words,
      max_length=max_length,
    )
    overall = segmented["overall"]
    ai_prob = overall["prob_generated"]
    human_prob = overall["prob_human"]
    details = {
      "prob_generated": overall["prob_generated"],
      "prob_generated_std": overall.get("prob_generated_std", 0.0),
      "prob_human": overall["prob_human"],
      "prob_human_std": overall.get("prob_human_std", 0.0),
      "prob_generated_raw": overall.get("prob_generated_raw", overall["prob_generated"]),
      "prob_human_raw": overall.get("prob_human_raw", overall["prob_human"]),
      "prob_entropy": overall.get("prob_entropy"),
      "prob_variation_ratio": overall.get("prob_variation_ratio"),
      "mc_dropout_passes": segmented.get("mc_dropout_passes"),
      "temperature": segmented.get("temperature"),
    }
  else:
    scores = predict_proba(text, return_details=True)
    ai_prob = scores["prob_generated"]
    human_prob = scores["prob_human"]
    details = {
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
    }

  ai_prob_pct = round(ai_prob * 100, 2)
  human_prob_pct = round(human_prob * 100, 2)
  response = {
    "text": text,
    "ai_probability": ai_prob_pct,
    "human_probability": human_prob_pct,
    "details": details,
  }

  if wants_segments:
    response["overall"] = segmented["overall"]
    response["segments"] = segmented["segments"]
    response["segment_params"] = segmented["params"]
    response["mc_dropout_passes"] = segmented.get("mc_dropout_passes")
    response["temperature"] = segmented.get("temperature")
    if segmented.get("mc_dropout_passes") and segmented["mc_dropout_passes"] > 1:
      response["ai_probability_std"] = round(overall.get("prob_generated_std", 0.0) * 100, 2)
      response["human_probability_std"] = round(overall.get("prob_human_std", 0.0) * 100, 2)
      response["uncertainty_entropy"] = overall.get("prob_entropy")
      response["uncertainty_variation_ratio"] = overall.get("prob_variation_ratio")
  else:
    if details["mc_dropout_passes"] and details["mc_dropout_passes"] > 1:
      response["ai_probability_std"] = round(details["prob_generated_std"] * 100, 2)
      response["human_probability_std"] = round(details["prob_human_std"] * 100, 2)
      response["uncertainty_entropy"] = details["prob_entropy"]
      response["uncertainty_variation_ratio"] = details["prob_variation_ratio"]
  
  return response, ai_prob_pct

def helper_to_save_into_db(text, ai_prob_pct, user_id):
  try:
    database = db.get_database("factify")
    collection = database["analisys"]
    doc = {
        "text": text,
        "ai_probability": ai_prob_pct,
        "user_id": user_id
    }
    collection.insert_one(doc)
  except Exception as e:
    current_app.logger.exception(f"MongoDB insert failed: {e}")

@nlp_bp.route("/predict", methods=["POST"])
def predict_endpoint():
  payload = request.get_json(silent=True) or {}
  text = str(payload.get("text", "")).strip()

  response, ai_prob_pct = helper_to_predict(
    text,
    detailed_raw=payload.get("detailed"),
    segment_params_raw=payload.get("segment_params"),
  )

  helper_to_save_into_db(
    text,
    ai_prob_pct,
    user_id=str(payload.get("user_id", "")).strip() or None,
  )
  
  return jsonify(response)

@nlp_bp.route("/predict_file", methods=["POST"])
def predict_file_endpoint():
  print("Przyjałem do odbioru")
  if "file" not in request.files:
    raise BadRequest("No file part in the request.")
  
  file = request.files["file"]
  if file.filename == "":
    raise BadRequest("No selected file.")
  print("zaczałem extract")
  try:
    text = extract_text(file, filename=file.filename)
    print("Skonczylem extract")
  except Exception as e:
    current_app.logger.exception(f"Text extraction failed: {e}")
    raise InternalServerError("Failed to extract text from the uploaded file.")

  print(text)
  payload = request.form or {}
  response, ai_prob_pct = helper_to_predict(
    text,
    detailed_raw=payload.get("detailed"),
    segment_params_raw=payload.get("segment_params"),
  )
  print("Skonczylem predict")
  print("Zapisuje do bazy")
  helper_to_save_into_db(
    text,
    ai_prob_pct,
    user_id=str(payload.get("user_id", "")).strip() or None,
  )
  print("Zapisalem do bazy")
  return jsonify(response)

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