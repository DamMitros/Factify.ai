from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest, InternalServerError
from PIL import Image
import io

from image_detection.detector import ImageDetector

image_bp = Blueprint("image", __name__)

# Inicjalizacja detektora (singleton)
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


@image_bp.route("/detect", methods=["POST"])
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
        
        # Zwracamy wynik
        return jsonify({
            "filename": file.filename,
            "predictions": result,
            "is_ai": result["ai"] > result["real"],
            "confidence": max(result["ai"], result["real"])
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise InternalServerError(f"Błąd podczas analizy obrazu: {str(e)}")


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
