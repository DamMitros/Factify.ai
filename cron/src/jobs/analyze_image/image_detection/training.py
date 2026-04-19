import torch
from torch import nn, optim
from torch.utils.data import DataLoader, random_split, Dataset
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report
import json

from detector.config import (
    DATA_DIR, BATCH_SIZE, EPOCHS, LEARNING_RATE, PATIENCE, 
    DEVICE, TRAIN_TRANSFORM, VAL_TRANSFORM, MODELS_DIR, BEST_MODEL_PATH,
    REPORTS_DIR, CONFUSION_MATRIX_V2, CLASSIFICATION_REPORT_V2, FINAL_MODEL_PATH_V2,
    BEST_MODEL_PATH_V2
)
from detector.model_utils import create_model, save_model, load_model

TRAIN_FROM_SCRATCH = True

try:
    from datasets import load_dataset
except ImportError:
    print("Błąd: Biblioteka 'datasets' nie jest zainstalowana. Uruchom: pip install datasets")
    raise

# Ładowanie danych z Hugging Face
print("Ładuję zbiór danych z Hugging Face...")
dataset_hf_full = load_dataset("Hemg/AI-Generated-vs-Real-Images-Datasets", split='train')

MAX_SAMPLES = 20000
if len(dataset_hf_full) > MAX_SAMPLES:
    print(f"Ograniczam zbiór z {len(dataset_hf_full)} do {MAX_SAMPLES} losowych zdjęć...")
    dataset_hf = dataset_hf_full.shuffle(seed=42).select(range(MAX_SAMPLES))
else:
    dataset_hf = dataset_hf_full

class HFDatasetWrapper(Dataset):
    """Wrapper dla Hugging Face Dataset do użycia z PyTorch."""
    def __init__(self, hf_dataset):
        self.dataset = hf_dataset
        self.class_names = ['ai', 'real']
        
    def __len__(self):
        return len(self.dataset)
        
    def __getitem__(self, idx):
        item = self.dataset[idx]
        return item['image'], item['label']

dataset_full = HFDatasetWrapper(dataset_hf)
class_names = dataset_full.class_names
print(f"Załadowano {len(dataset_full)} obrazów z HF.")

print(f"Używam urządzenia: {DEVICE}")
print(f"Katalog na modele: {MODELS_DIR}")

def plot_confusion_matrix(y_true, y_pred, classes, save_path):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(10, 8))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title("Confusion Matrix")
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = 'd'
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(j, i, format(cm[i, j], fmt),
                     horizontalalignment="center",
                     color="white" if cm[i, j] > thresh else "black")

    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    print(f"✓ Confusion matrix zapisana: {save_path}")

# Dataset z transformacjami
class TransformDataset(Dataset):
    """Aplikuje transformacje na obrazach z HF Dataset."""
    def __init__(self, hf_dataset, indices, transform):
        self.hf_dataset = hf_dataset
        self.indices = indices
        self.transform = transform
        
    def __len__(self):
        return len(self.indices)
        
    def __getitem__(self, idx):
        actual_idx = self.indices[idx]
        item = self.hf_dataset[actual_idx]
        image = item['image']
        label = item['label']
        
        # Upewnij się, że to RGB PIL Image
        if not hasattr(image, 'mode') or image.mode != 'RGB':
            image = image.convert('RGB')
            
        if self.transform:
            image = self.transform(image)
            
        return image, label

# Podział na train/val
print(f"Dzielę zbiór {len(dataset_hf)} obrazów na train/val...")
indices = list(range(len(dataset_hf)))
train_size = int(0.8 * len(indices))
val_size = len(indices) - train_size
train_indices, val_indices = random_split(indices, [train_size, val_size])

# Zastosowanie transformacji
train_ds = TransformDataset(dataset_hf, train_indices.indices, TRAIN_TRANSFORM)
val_ds = TransformDataset(dataset_hf, val_indices.indices, VAL_TRANSFORM)

train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False)

# Model - opcja załadowania istniejącego
if not TRAIN_FROM_SCRATCH and BEST_MODEL_PATH.exists():
    print(f"Wykryto istniejący model, ładuję do dalszego treningu: {BEST_MODEL_PATH}")
    model = load_model(BEST_MODEL_PATH, device=DEVICE)
    for param in model.parameters():
        param.requires_grad = True
    load_success = True
else:
    if TRAIN_FROM_SCRATCH:
        print("Trening od zera (wymuszony przez flagę TRAIN_FROM_SCRATCH).")
    else:
        print("Brak istniejącego modelu, tworzę nowy model.")
    model = create_model()
    model.to(DEVICE)
    load_success = False

print(f"Model: {model.__class__.__name__}")

criterion = nn.CrossEntropyLoss()
current_lr = LEARNING_RATE if not load_success else LEARNING_RATE/10
optimizer = optim.Adam(model.parameters(), lr=current_lr)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.1, patience=2)

# Trening
best_acc = 0
patience_counter = 0

print(f"\nRozpoczynanie treningu: {EPOCHS} epok")
for epoch in range(EPOCHS):
    model.train()
    train_loss = 0
    
    for images, labels in tqdm(train_loader, desc=f"Epoch {epoch+1}/{EPOCHS}"):
        images, labels = images.to(DEVICE), labels.to(DEVICE)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        train_loss += loss.item()

    # Walidacja
    model.eval()
    val_loss = 0
    correct, total = 0, 0
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            outputs = model(images)
            loss = criterion(outputs, labels)
            val_loss += loss.item()
            
            preds = outputs.argmax(1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    avg_train_loss = train_loss / len(train_loader)
    avg_val_loss = val_loss / len(val_loader)
    acc = correct / total
    
    print(f"Epoch {epoch+1}: train_loss={avg_train_loss:.4f}, val_loss={avg_val_loss:.4f}, val_acc={acc:.4f}")
    
    scheduler.step(avg_val_loss)
    
    if acc > best_acc:
        best_acc = acc
        save_model(model, BEST_MODEL_PATH_V2)
        print(f"  ✓ Nowy najlepszy model! acc={acc:.3f}")
        patience_counter = 0
        
        plot_confusion_matrix(all_labels, all_preds, class_names, CONFUSION_MATRIX_V2)
        report = classification_report(all_labels, all_preds, target_names=class_names, output_dict=True)
        with open(CLASSIFICATION_REPORT_V2, "w") as f:
            json.dump(report, f, indent=4)
    else:
        patience_counter += 1
    
    if not load_success and epoch == 4:
        print("  → Odmrażam backbone dla lepszego fine-tuningu...")
        for param in model.features.parameters():
            param.requires_grad = True

    if patience_counter >= PATIENCE:
        print(f"Early stopping: brak poprawy przez {PATIENCE} epok")
        break

final_model_path = FINAL_MODEL_PATH_V2
save_model(model, final_model_path)
print(f"\n✓ Model z ostatniej epoki: {final_model_path}")
print(f"✓ Najlepszy model (acc={best_acc:.3f}): {BEST_MODEL_PATH_V2}")


def predict(image_path):
    """Testowa funkcja predykcji."""
    from detector.inference import ImageDetector
    detector = ImageDetector()
    return detector.predict(image_path)