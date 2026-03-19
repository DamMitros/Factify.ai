import pytest, csv
from pathlib import Path
import torch
from transformers import AutoTokenizer, RobertaForSequenceClassification

@pytest.fixture(scope="session")
def model_path():
    """Ścieżka do wytrenowanego modelu"""
    base_path = Path(__file__).parent.parent
    return base_path / "artifacts" / "models" / "roberta_finetuned.pt"

@pytest.fixture(scope="session")
def artifacts_dir():
    """Katalog artifacts"""
    return Path(__file__).parent.parent / "artifacts"

@pytest.fixture(scope="session")
def model(model_path):
    """Wczytuje wytrenowany model z pliku. Dostępny dla wszystkich testów."""
    try:
        model = RobertaForSequenceClassification.from_pretrained('roberta-base', num_labels=2)
        
        checkpoint = torch.load(model_path, map_location=torch.device('cpu'))
        model.load_state_dict(checkpoint['model_state_dict'])
        
        model.eval()
        return model
    except Exception as e:
        pytest.fail(f"Nie udało się załadować modelu z {model_path}: {e}")


@pytest.fixture(scope="session")
def tokenizer():
    """Wczytuje tokenizer. Dostępny dla wszystkich testów."""
    return AutoTokenizer.from_pretrained('roberta-base')

@pytest.fixture(scope="session")
def failure_reporter():
    """
    Zbiera informacje o błędnych predykcjach i zapisuje je do pliku CSV
    na koniec sesji testowej.
    """
    failures = []
    yield failures

    if failures:
        report_dir = Path("./src/nlp/tests/evaluation")
        report_dir.mkdir(exist_ok=True, parents=True)
        
        report_file = report_dir / "model_prediction_failures_human.csv"
        
        with open(report_file, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=[
                "text_fragment",
                "description", 
                "expected_class", 
                "predicted_class",
                "confidence_human_percent",
                "confidence_ai_percent"
            ])
            writer.writeheader()
            writer.writerows(failures)
        
        print(f"\n\nRaport błędów zapisany do: {report_file.absolute()}")
        print(f"Liczba błędnych predykcji: {len(failures)}")


@pytest.fixture(scope="session")
def failure_reporter_mix():
    """
    Zbiera informacje o błędnych predykcjach dla testów mieszanych (human + AI)
    i zapisuje je do osobnego pliku CSV.
    """
    failures = []
    yield failures

    if failures:
        report_dir = Path("./src/nlp/tests/evaluation")
        report_dir.mkdir(exist_ok=True, parents=True)
        
        report_file = report_dir / "model_prediction_failures_mixed2.csv"
        
        with open(report_file, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=[
                "text_fragment",
                "description",
                "expected_class",
                "expected_label",
                "predicted_class",
                "predicted_label",
                "confidence_human_percent",
                "confidence_ai_percent"
            ])
            writer.writeheader()
            writer.writerows(failures)
        
        print(f"\n\nRaport błędów (mixed) zapisany do: {report_file.absolute()}")
        print(f"Liczba błędnych predykcji: {len(failures)}")