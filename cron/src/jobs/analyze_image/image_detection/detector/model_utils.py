import torch
from torchvision import models
from torch import nn
from pathlib import Path


def create_model(num_classes=2, pretrained=True):
    """
    Utwórz model EfficientNet-B0 dla klasyfikacji AI vs Real.
    
    Args:
        num_classes: Liczba klas (domyślnie 2: ai_generated, real)
        pretrained: Czy użyć pretrenowanych wag ImageNet
        
    Returns:
        model: Skonfigurowany model PyTorch
    """
    weights = models.EfficientNet_B0_Weights.DEFAULT if pretrained else None
    model = models.efficientnet_b0(weights=weights)
    
    # Zamroź backbone (odmrożymy później podczas treningu)
    for param in model.features.parameters():
        param.requires_grad = False
    
    # Zamień klasyfikator (w EfficientNet-B0 to model.classifier)
    num_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.2, inplace=True),
        nn.Linear(num_features, num_classes)
    )
    
    return model


def save_model(model, save_path):
    """
    Zapisz model do pliku.
    
    Args:
        model: Model PyTorch
        save_path: Ścieżka zapisu
    """
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    
    torch.save(model.state_dict(), save_path)
    print(f"✓ Model zapisany: {save_path}")


def load_model(model_path, device='cpu'):
    """
    Załaduj model z pliku z obsługą prefiksów i niezgodności kluczy.
    
    Args:
        model_path: Ścieżka do modelu
        device: Urządzenie (cpu/cuda)
        
    Returns:
        model: Załadowany model
    """
    model = create_model(pretrained=False)
    try:
        state_dict = torch.load(model_path, map_location=device)
    except Exception as e:
        raise RuntimeError(f"Błąd podczas ładowania pliku modelu {model_path}: {e}")

    if isinstance(state_dict, dict):
        # Usuń 'model.' lub 'module.' i klucze num_batches_tracked
        new_state_dict = {}
        for k, v in state_dict.items():
            name = k.replace("model.", "").replace("module.", "")
            if "num_batches_tracked" not in name:
                new_state_dict[name] = v
        
        try:
            model.load_state_dict(new_state_dict, strict=True)
        except RuntimeError as e:
            print(f"Direct load failed: {e}. Trying strict=False...")
            model.load_state_dict(new_state_dict, strict=False)
    else:
        model = state_dict

    model.to(device)
    model.eval()
    
    return model