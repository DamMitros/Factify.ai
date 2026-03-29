from datetime import datetime

from context import TaskContext
from types_ import TaskPayload
from .nlp.detector.model_utils import load_model_artifacts
from .helpers import helper_to_predict


def task(payload: TaskPayload, ctx: TaskContext):
    text = payload["text"]
    user_id = payload["user_id"]

    response, ai_prob_pct = helper_to_predict(text)

    database = ctx.db.get_database("factify_ai")
    collection = database["analysis"]
    doc = {
        "text": text,
        "ai_probability": ai_prob_pct,
        "user_id": user_id,
        "timestamp": datetime.utcnow(),
        "segments": response.get("segments") if response else None,
        "overall": response.get("overall") if response else None,
        "action": "text_analysis"
    }
    result = collection.insert_one(doc)

    return result.inserted_id


print("Loading NLP model artifacts...")
try:
    load_model_artifacts()
    print("NLP model artifacts loaded successfully.")
except Exception as e:
    print(f"Error loading NLP model artifacts: {e}")
