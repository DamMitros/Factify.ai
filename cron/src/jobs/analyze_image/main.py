import io, base64

from PIL import Image
from datetime import datetime

from context import TaskContext
from types_ import TaskPayload

from .image_detection.detector import ImageDetector
from config import DB_NAME, COL_ANALYSIS_AI_IMAGE

_detector = None

def get_detector():
  global _detector
  if _detector is None:
      _detector = ImageDetector()
  return _detector


def generate_thumbnail(image, size=(300, 300)):
  try:
    thumb = image.copy()
    thumb.thumbnail(size)
    buffered = io.BytesIO()
    if thumb.mode in ("RGBA", "P"):
      thumb = thumb.convert("RGB")
    thumb.save(buffered, format="JPEG", quality=85)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{img_str}"
  except Exception as e:
    print(f"Error generating thumbnail: {e}")
    return None
  
def task(payload: TaskPayload, ctx: TaskContext):
  filename = payload["filename"]
  image_base64 = payload["image_base64"]
  user_id = payload["user_id"]

  image_bytes = base64.b64decode(image_base64)
  image = Image.open(io.BytesIO(image_bytes))

  detector = get_detector()
  result = detector.predict(image)

  ai_prob_pct = round(result["ai"] * 100, 2)
  image_preview = generate_thumbnail(image)

  database = ctx.db.get_database(DB_NAME)
  collection = database[COL_ANALYSIS_AI_IMAGE]

  doc = {
    "filename": filename,
    "ai_probability": ai_prob_pct,
    "user_id": user_id,
    "timestamp": datetime.utcnow(),
    "image_preview": image_preview,
    "overall": {
      "label": "AI" if result.get("ai", 0) > result.get("real", 0) else "Real",
      "confidence": max(result.get("ai", 0), result.get("real", 0))
    },
    "raw_predictions": result,
    "action": "image_analysis"    
  }

  db_result = collection.insert_one(doc)
  return db_result.inserted_id