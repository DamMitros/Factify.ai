import torch
from torch import nn, optim
from torch.utils.data import DataLoader, random_split, Dataset
from torchvision import datasets
from tqdm import tqdm

from detector.config import (
    DATA_DIR, BATCH_SIZE, EPOCHS, LEARNING_RATE, PATIENCE, 
    DEVICE, TRAIN_TRANSFORM, VAL_TRANSFORM, MODELS_DIR, BEST_MODEL_PATH
)
from detector.model_utils import create_model, save_model

print(f"Używam urządzenia: {DEVICE}")
print(f"Katalog z danymi: {DATA_DIR}")
print(f"Katalog na modele: {MODELS_DIR}")


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

# Model
model = create_model()
print(f"Model utworzony: {model.__class__.__name__}")

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.classifier.parameters(), lr=LEARNING_RATE)

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
    correct, total = 0, 0

    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            preds = model(images).argmax(1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

    acc = correct / total
    print(f"Epoch {epoch+1}: train_loss={train_loss:.3f}, val_acc={acc:.3f}")
    
    # Zapisanie najlepszego modelu
    if acc > best_acc:
        best_acc = acc
        save_model(model, BEST_MODEL_PATH)
        print(f"  ✓ Nowy najlepszy model! acc={acc:.3f}")
        patience_counter = 0
    else:
        patience_counter += 1
    
    # Fine-tuning - odmrożenie backbone po kilku epokach
    if epoch == 4:
        print("  → Odmrażam backbone dla lepszego fine-tuningu...")
        for param in model.features.parameters():
            param.requires_grad = True
        optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE/10)
    
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