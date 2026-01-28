from pathlib import Path
import torch
from torchvision import transforms


BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "artifacts" / "models"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
REPORTS_DIR = ARTIFACTS_DIR / "reports"


MODELS_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACTS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)


BEST_MODEL_PATH = MODELS_DIR / "ai_vs_real_best.pth"


BATCH_SIZE = 32
EPOCHS = 35
LEARNING_RATE = 0.001
PATIENCE = 10


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


TRAIN_TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

VAL_TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])


CLASS_NAMES = ['ai_generated', 'real']