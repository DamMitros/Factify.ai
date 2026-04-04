import torch
import pytest
import csv
import sys
import random
from pathlib import Path

def load_mixed_texts(file_path):
    """Wczytuje teksty wraz z ich etykietami z pliku CSV"""
    max_int = sys.maxsize
    while True:
        try:
            csv.field_size_limit(max_int)
            break
        except OverflowError:
            max_int = int(max_int / 10)
    
    test_cases = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)  
            for i, row in enumerate(reader):
                text = row['text']
                
                expected_class = int(float(row['generated']))
                
                if len(text) > 30000:
                    text = text[:30000]
                
                test_cases.append({
                    'text': text,
                    'expected_class': expected_class,
                    'row_number': i + 2,
                    'label': 'Human' if expected_class == 0 else 'AI'  
                })
    except FileNotFoundError:
        pytest.fail(f"Plik z danymi testowymi nie został znaleziony: {file_path}")
    except KeyError as e:
        pytest.fail(f"Brak wymaganej kolumny w pliku CSV: {e}")
    
    return test_cases

MIXED_TEXTS_FILE = Path("./src/nlp/tests/resources/AI_Human.csv")
ALL_TEST_CASES = load_mixed_texts(MIXED_TEXTS_FILE)

random.seed(42)
SELECTED_CASES = random.sample(ALL_TEST_CASES, min(300, len(ALL_TEST_CASES)))

@pytest.mark.parametrize("test_case", SELECTED_CASES)
def test_model_predictions_on_mixed_texts(model, tokenizer, test_case, failure_reporter_mix):
    """
    Testuje predykcje modelu na zestawie tekstów ludzkich i AI.
    Porównuje klasę z CSV bezpośrednio z predykcją modelu.
    Model: 0=Human, 1=AI
    CSV: 0=Human, 1=AI
    """
    text = test_case['text']
    expected_class = test_case['expected_class']
    description = f"Wiersz {test_case['row_number']} ({test_case['label']})"

    if not text.strip():
        pytest.skip("Pusty wiersz w pliku CSV.")

    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)

    with torch.no_grad():
        outputs = model(**inputs)

    probabilities = torch.softmax(outputs.logits, dim=-1)[0]
    predicted_class = torch.argmax(probabilities).item()
    
    if predicted_class != expected_class:
        failure_info = {
            "text_fragment": text[:200] + "...",
            "description": description,
            "expected_class": expected_class,
            "expected_label": test_case['label'],
            "predicted_class": predicted_class,
            "predicted_label": 'Human' if predicted_class == 0 else 'AI',
            "confidence_human_percent": f"{probabilities[0].item()*100:.2f}%",  
            "confidence_ai_percent": f"{probabilities[1].item()*100:.2f}%"     
        }
        failure_reporter_mix.append(failure_info)
        
        pytest.fail(
            f"Błąd dla przypadku: {description}. "
            f"Oczekiwano: {test_case['label']} (klasa {expected_class}), "
            f"otrzymano: {'Human' if predicted_class == 0 else 'AI'} (klasa {predicted_class})."
        )