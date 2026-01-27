from flask import Blueprint, jsonify, request, current_app, g
from werkzeug.exceptions import BadRequest, InternalServerError
from PIL import Image
import io
import base64
from datetime import datetime

from image_detection.detector import ImageDetector
from common.python import db
from keycloak_client import require_auth_optional

image_bp = Blueprint("image", __name__)


_detector = None


def get_detector():
    """Zwraca singleton instancję ImageDetector."""
    global _detector
    if _detector is None:
        try:
            _detector = ImageDetector()
        except FileNotFoundError as e:
            raise InternalServerError(f"Model nie znaleziony. Pobierz model z releases: {str(e)}")
    return _detector


def generate_thumbnail(image, size=(300, 300)):
    """Generuje miniaturkę Base64 z obrazu PIL."""
    try:
        thumb = image.copy()
        thumb.thumbnail(size)
        buffered = io.BytesIO()
        # Konwertujemy do RGB jeśli obraz ma kanał alfa (PNG), aby zapisać jako JPEG
        if thumb.mode in ("RGBA", "P"):
            thumb = thumb.convert("RGB")
        thumb.save(buffered, format="JPEG", quality=85)
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{img_str}"
    except Exception as e:
        current_app.logger.warning(f"Failed to generate thumbnail: {e}")
        return None


def helper_to_save_image_to_db(filename, ai_prob_pct, user_id, image_preview=None, result_data=None):
    """Zapisuje wynik analizy obrazu do bazy danych (mirror nlp.py logic)."""
    try:
        database = db.get_database("factify")
        collection = database["image_analysis"]
        doc = {
            "filename": filename,
            "ai_probability": ai_prob_pct,
            "user_id": user_id,
            "timestamp": datetime.utcnow(),
            "image_preview": image_preview,
            "overall": {
                "label": "AI" if result_data.get("ai", 0) > result_data.get("real", 0) else "Real",
                "confidence": max(result_data.get("ai", 0), result_data.get("real", 0))
            },
            "raw_predictions": result_data,
            "action": "image_analysis"
        }
        collection.insert_one(doc)
    except Exception as e:
        current_app.logger.exception(f"MongoDB insert failed for image: {e}")


@image_bp.route("/detect", methods=["POST"])
@require_auth_optional
def detect_ai_image():
    """
    Wykrywa czy obraz został wygenerowany przez AI.
    
    Expects:
        - Multipart/form-data z plikiem obrazu w polu 'file'
    
    Returns:
        JSON z prawdopodobieństwami i wynikiem klasyfikacji
    """
    if "file" not in request.files:
        raise BadRequest("Brak pliku w żądaniu. Użyj pola 'file'.")
    
    file = request.files["file"]
    
    if file.filename == "":
        raise BadRequest("Nie wybrano pliku.")
    
    try:
        # Wczytanie obrazu z przesłanego pliku
        contents = file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Predykcja
        detector = get_detector()
        result = detector.predict(image)
        
        ai_prob_pct = round(result["ai"] * 100, 2)
        
        # Generowanie miniaturki Base64
        image_preview = generate_thumbnail(image)
        
        user_id = None
        if g.user:
            user_id = g.user.get("sub")
            print(f"Authenticated user_id for image prediction: {user_id}")
        else:
            print("No authenticated user for image prediction")

        # Zapis do bazy danych
        helper_to_save_image_to_db(
            filename=file.filename,
            ai_prob_pct=ai_prob_pct,
            user_id=user_id,
            image_preview=image_preview,
            result_data=result
        )

        # Zwracamy wynik
        return jsonify({
            "filename": file.filename,
            "predictions": result,
            "is_ai": result["ai"] > result["real"],
            "confidence": max(result["ai"], result["real"]),
            "image_preview": image_preview
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise InternalServerError(f"Błąd podczas analizy obrazu: {str(e)}")


@image_bp.route("/predictions/<user_id>", methods=["GET"])
def get_image_predictions_by_user(user_id: str):
    """Pobiera historię analiz obrazów użytkownika (mirror nlp.py logic)."""
    user_id = (user_id or "").strip()
    if not user_id:
        raise BadRequest("Missing user_id")

    try:
        database = db.get_database("factify")
        collection = database["image_analysis"]

        cursor = collection.find({"user_id": user_id}).sort("timestamp", -1)

        results = [
            {
                "id": str(doc.get("_id")),
                "filename": doc.get("filename"),
                "ai_probability": doc.get("ai_probability"),
                "human_probability": 100 - doc.get("ai_probability", 0),
                "created_at": doc.get("timestamp"),
                "image_preview": doc.get("image_preview"),
                "overall": doc.get("overall"),
                "confidence": doc.get("overall", {}).get("confidence"),
                "type": "image"
            }
            for doc in cursor
        ]

        return jsonify(results)
    except Exception as e:
        current_app.logger.exception("Failed to fetch image predictions for user %s: %s", user_id, e)
        raise InternalServerError("Failed to fetch image predictions")


@image_bp.route("/health", methods=["GET"])
def health_check():
    """Sprawdza czy model jest załadowany i gotowy."""
    try:
        get_detector()
        return jsonify({"status": "ok", "model_loaded": True})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "model_loaded": False, "error": str(e)}), 500
