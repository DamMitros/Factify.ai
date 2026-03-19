from flask import Blueprint, jsonify, g
from keycloak_client import require_auth
from datetime import datetime

from common.python import db
from config import DB_NAME, COL_ANALYSIS_AI_TEXT, COL_ANALYSIS_AI_IMAGE

history_bp = Blueprint("history", __name__)

@history_bp.route("/my-analyses", methods=["GET"])
@require_auth
def get_my_analyses():
  user_id = g.user.get("sub")  
  db_instance = db.get_database(DB_NAME)
  
  text_results = list(db_instance[COL_ANALYSIS_AI_TEXT].find({"user_id": user_id}).sort("created_at", -1).limit(20))
  image_results = list(db_instance[COL_ANALYSIS_AI_IMAGE].find({"user_id": user_id}).sort("timestamp", -1).limit(20))

  user_analyses_history = []
  
  for doc in text_results:
    overall = doc.get("overall", {})
    label = overall.get("label") or doc.get("label") or doc.get("prediction") or "Unknown"
    score = overall.get("confidence") or overall.get("score") or doc.get("score") or doc.get("confidence") or 0
    text = doc.get("text") or doc.get("content") or ""

    try:
      score = float(score)
    except (ValueError, TypeError):
      score = 0.0

    user_analyses_history.append({
      "id": str(doc["_id"]),
      "text_preview": text[:80] + "..." if text else "No text content",
      "label": label,
      "score": score,
      "type": "text",
      "created_at": doc.get("timestamp") or doc.get("created_at")
    })

  for doc in image_results:
    overall = doc.get("overall", {})
    label = overall.get("label") or "Unknown"
    score = overall.get("confidence") or doc.get("ai_probability", 0) / 100 or 0
    filename = doc.get("filename") or "image"

    try:
      score = float(score)
    except (ValueError, TypeError):
      score = 0.0

    user_analyses_history.append({
      "id": str(doc["_id"]),
      "text_preview": f"Image Analysis: {filename}",
      "label": label,
      "score": score,
      "type": "image",
      "image_preview": doc.get("image_preview"),
      "created_at": doc.get("timestamp")
    })

  user_analyses_history.sort(key=lambda x: x["created_at"] if x["created_at"] else datetime.min, reverse=True)
  
  return jsonify(user_analyses_history[:20])