import torch
from torch import nn, optim
from torch.utils.data import DataLoader, random_split, Dataset
from torchvision import datasets
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report
import json

from detector.config import (
    DATA_DIR, BATCH_SIZE, EPOCHS, LEARNING_RATE, PATIENCE, 
    DEVICE, TRAIN_TRANSFORM, VAL_TRANSFORM, MODELS_DIR, BEST_MODEL_PATH,
    REPORTS_DIR
)
from detector.model_utils import create_model, save_model, load_model

print(f"Używam urządzenia: {DEVICE}")
print(f"Katalog z danymi: {DATA_DIR}")
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

class TransformSubset(Dataset):
    """Dataset wrapper do aplikowania różnych transformacji na train/val."""
    def __init__(self, base_dataset, indices, transform):
        self.base_dataset = base_dataset
        self.indices = indices
        self.transform = transform
        
    def __getitem__(self, idx):
        img_path, label = self.base_dataset.samples[self.indices[idx]]
        img = self.base_dataset.loader(img_path)
        
        if self.transform:
            img = self.transform(img)
        
        return img, label
    
    def __len__(self):
        return len(self.indices)


# Dataset bez augmentacji dla podziału
dataset_raw = datasets.ImageFolder(root=str(DATA_DIR))
class_names = dataset_raw.classes
print("MAPA KLAS:", dataset_raw.class_to_idx)

# Podział na train/val
train_size = int(0.8 * len(dataset_raw))
val_size = len(dataset_raw) - train_size
train_indices, val_indices = random_split(range(len(dataset_raw)), [train_size, val_size])

# Zastosowanie transformacji
train_ds = TransformSubset(dataset_raw, train_indices.indices, TRAIN_TRANSFORM)
val_ds = TransformSubset(dataset_raw, val_indices.indices, VAL_TRANSFORM)

train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False)

# Model - opcja załadowania istniejącego
if BEST_MODEL_PATH.exists():
    print(f"Wykryto istniejący model, ładuję do dalszego treningu: {BEST_MODEL_PATH}")
    model = load_model(BEST_MODEL_PATH, device=DEVICE)
    # Odmrożenie parametrów, bo zakładamy że chcemy go dotrenować
    for param in model.parameters():
        param.requires_grad = True
else:
    print("Tworzę nowy model.")
    model = create_model()
    model.to(DEVICE)

print(f"Model: {model.__class__.__name__}")

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE/10 if BEST_MODEL_PATH.exists() else LEARNING_RATE)
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
    
    # Zapisanie najlepszego modelu
    if acc > best_acc:
        best_acc = acc
        save_model(model, BEST_MODEL_PATH)
        print(f"  ✓ Nowy najlepszy model! acc={acc:.3f}")
        patience_counter = 0
        
        # Generuj raport i macierz dla najlepszego modelu
        plot_confusion_matrix(all_labels, all_preds, class_names, REPORTS_DIR / "confusion_matrix_best.png")
        report = classification_report(all_labels, all_preds, target_names=class_names, output_dict=True)
        with open(REPORTS_DIR / "classification_report_best.json", "w") as f:
            json.dump(report, f, indent=4)
    else:
        patience_counter += 1
    
    # Fine-tuning logic dla nowego modelu
    if not BEST_MODEL_PATH.exists() and epoch == 4:
        print("  → Odmrażam backbone dla lepszego fine-tuningu...")
        for param in model.features.parameters():
            param.requires_grad = True
        # Nie resetujemy całkiem optimizera, ale scheduler i LR mogą być skorygowane
    
    # Early stopping
    if patience_counter >= PATIENCE:
        print(f"Early stopping: brak poprawy przez {PATIENCE} epok")
        break

# Zapisanie ostatniego modelu
final_model_path = MODELS_DIR / "ai_vs_real_final.pth"
save_model(model, final_model_path)
print(f"\n✓ Model z ostatniej epoki: {final_model_path}")
print(f"✓ Najlepszy model (acc={best_acc:.3f}): {BEST_MODEL_PATH}")


# Funkcja do testowania
def predict(image_path):
    """Testowa funkcja predykcji."""
    from detector.inference import ImageDetector
    detector = ImageDetector()
    return detector.predict(image_path)