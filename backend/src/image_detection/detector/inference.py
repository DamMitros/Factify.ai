import torch
from PIL import Image
from pathlib import Path

# ZMIANA: użyj względnych importów
from .config import DEVICE, VAL_TRANSFORM, CLASS_NAMES, BEST_MODEL_PATH
from .model_utils import create_model


class ImageDetector:
    """Klasa do wykrywania czy obraz jest AI-generated czy rzeczywisty."""
    
    def __init__(self, model_path=None):
        """
        Args:
            model_path: Ścieżka do modelu. Jeśli None, użyje BEST_MODEL_PATH.
        """
        self.model_path = Path(model_path) if model_path else BEST_MODEL_PATH
        self.device = DEVICE
        self.transform = VAL_TRANSFORM
        self.class_names = CLASS_NAMES
        
        # Załaduj model
        self.model = self._load_model()
        
    def _load_model(self):
        """Załaduj wytrenowany model."""
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model nie został znaleziony: {self.model_path}\n"
                f"Wytrenuj model używając training.py lub pobierz z releases."
            )
        
        model = create_model()
        state_dict = torch.load(self.model_path, map_location=self.device)
        
        # FIX: Check if we are loading a state_dict or the whole model
        if isinstance(state_dict, dict):
            # Try to load state_dict, but if it fails due to architecture mismatch,
            # it might be because the model was saved differently
            try:
                model.load_state_dict(state_dict)
            except RuntimeError as e:
                print(f"Direct load failed: {e}. Trying fuzzy load...")
                # Handle potential key mismatch (e.g. model. prefix)
                new_state_dict = {}
                for k, v in state_dict.items():
                    name = k.replace("model.", "") # remove `model.` prefix if it exists
                    new_state_dict[name] = v
                model.load_state_dict(new_state_dict, strict=False)
        else:
            model = state_dict
            
        model.to(self.device)
        model.eval()
        
        print(f"✓ Model załadowany z: {self.model_path}")
        return model
    
    def predict(self, image):
        """
        Przewiduj czy obraz jest AI-generated czy rzeczywisty.
        
        Args:
            image: PIL.Image lub ścieżka do obrazu
            
        Returns:
            dict: {'ai': float, 'real': float} - prawdopodobieństwa
        """
        # Obsłuż zarówno ścieżkę jak i PIL.Image
        if isinstance(image, (str, Path)):
            image_path = Path(image)
            if not image_path.exists():
                raise FileNotFoundError(f"Obraz nie istnieje: {image_path}")
            image = Image.open(image_path).convert('RGB')
        elif not isinstance(image, Image.Image):
            raise TypeError(f"Oczekiwano PIL.Image lub ścieżkę, otrzymano: {type(image)}")
        
        # Upewnij się, że obraz jest w RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Przetwórz obraz
        image_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        # Predykcja
        with torch.no_grad():
            outputs = self.model(image_tensor)
            probabilities = torch.softmax(outputs, dim=1)[0]
        
        # Przygotuj wynik w formacie kompatybilnym z routes/image.py
        result = {
            'ai': probabilities[0].item(),  # ai_generated
            'real': probabilities[1].item()  # real
        }
        
        return result
    
    def predict_detailed(self, image):
        """
        Przewiduj z dodatkowymi szczegółami.
        
        Args:
            image: PIL.Image lub ścieżka do obrazu
            
        Returns:
            dict: {'class': str, 'confidence': float, 'probabilities': dict}
        """
        result = self.predict(image)
        
        predicted_class = 'ai_generated' if result['ai'] > result['real'] else 'real'
        confidence = max(result['ai'], result['real'])
        
        return {
            'class': predicted_class,
            'confidence': confidence,
            'probabilities': {
                'ai_generated': result['ai'],
                'real': result['real']
            }
        }
    
    def predict_batch(self, images):
        """
        Przewiduj dla wielu obrazów.
        
        Args:
            images: Lista PIL.Image lub ścieżek do obrazów
            
        Returns:
            list: Lista wyników dla każdego obrazu
        """
        results = []
        for image in images:
            try:
                result = self.predict(image)
                results.append(result)
            except Exception as e:
                results.append({'error': str(e)})
        
        return results