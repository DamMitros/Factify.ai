from transformers import AutoTokenizer, AutoModelForSequenceClassification
from pathlib import Path

MODEL_NAME = "roberta-base"
SAVE_DIR = Path(__file__).parent / ".." / "artifacts" / "base_model"


def download_and_save():
    print(f"Start pobierania bazowego modelu: {MODEL_NAME}")
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    tokenizer.save_pretrained(SAVE_DIR)

    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)
    model.save_pretrained(SAVE_DIR)
    print(f"Model bazowy zapisano w: {SAVE_DIR}")

download_and_save()
