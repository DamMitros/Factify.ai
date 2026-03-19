import torch
import pytest
import csv
import sys, random
from pathlib import Path

def load_all_texts(file_path):
    max_int = sys.maxsize
    while True:
        try:
            csv.field_size_limit(max_int)
            break
        except OverflowError:
            max_int = int(max_int / 10)
    
    texts = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)
            for row in reader:
                if len(row) >= 2:
                    text = row[1]
                    
                    if len(text) > 30000:
                        text = text[:30000]
                    texts.append(text)
                    
    except FileNotFoundError:
        pytest.fail(f"Plik z danymi testowymi nie został znaleziony: {file_path}")
    return texts

HUMAN_TEXTS_FILE = Path("./src/nlp/tests/resources/Shuffled_Human.csv")
ALL_HUMAN_TEXTS = load_all_texts(HUMAN_TEXTS_FILE)


random.seed(42)  
TEST_CASES_INDICES = random.sample(range(len(ALL_HUMAN_TEXTS)), min(300, len(ALL_HUMAN_TEXTS)))



EXPECTED_CLASS_HUMAN = 0

@pytest.mark.parametrize("text_index", TEST_CASES_INDICES)
def test_model_predictions_on_human_texts(model, tokenizer, text_index, failure_reporter):
    """
    Testuje predykcje modelu na zestawie tekstów ludzkich.
    W przypadku błędu, zapisuje informacje do raportu.
    """
    text = ALL_HUMAN_TEXTS[text_index]
    description = f"Wiersz {text_index + 2} z pliku {HUMAN_TEXTS_FILE.name}"

    if not text.strip():
        pytest.skip("Pusty wiersz w pliku CSV.")

    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)

    with torch.no_grad():
        outputs = model(**inputs)

    probabilities = torch.softmax(outputs.logits, dim=-1)[0]
    predicted_class = torch.argmax(probabilities).item()
    
    if predicted_class != EXPECTED_CLASS_HUMAN:
        failure_info = {
            "text_fragment": text[:200] + "...",
            "description": description,
            "expected_class": EXPECTED_CLASS_HUMAN,
            "predicted_class": predicted_class,
            "confidence_human_percent": f"{probabilities[0].item()*100:.2f}%", 
            "confidence_ai_percent": f"{probabilities[1].item()*100:.2f}%"   
        }
        failure_reporter.append(failure_info)
        
        pytest.fail(
            f"Błąd dla przypadku: {description}. "
            f"Oczekiwano klasy {EXPECTED_CLASS_HUMAN} (Human), otrzymano {predicted_class}."
        )