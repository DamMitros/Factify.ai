import pytest
import torch

class TestModelInference:
    """Testy sprawdzające strukturę i typy zwracane przez model."""

    def test_model_prediction_shape(self, model, tokenizer):
        """Testuje, czy model zwraca predykcje o poprawnym kształcie."""
        text = "This is a sample text for testing the model."
        inputs = tokenizer(text, return_tensors="pt")
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        # Zmień '2' jeśli masz inną liczbę etykiet
        assert outputs.logits.shape == (1, 2)

    def test_model_prediction_output_type(self, model, tokenizer):
        """Testuje, czy wyjście modelu jest tensorem typu float."""
        text = "Another test sentence."
        inputs = tokenizer(text, return_tensors="pt")

        with torch.no_grad():
            outputs = model(**inputs)

        assert isinstance(outputs.logits, torch.Tensor)
        assert outputs.logits.dtype == torch.float32