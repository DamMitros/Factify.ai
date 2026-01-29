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
    if pretrained:
        weights = models.EfficientNet_B0_Weights.DEFAULT
        model = models.efficientnet_b0(weights=weights)
    else:
        model = models.efficientnet_b0(weights=None)
    
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
    Załaduj model z pliku.
    
    Args:
        model_path: Ścieżka do modelu
        device: Urządzenie (cpu/cuda)
        
    Returns:
        model: Załadowany model
    """
    model = create_model()
    state_dict = torch.load(model_path, map_location=device)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    
    return model