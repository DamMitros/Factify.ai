import pytest
from src.nlp.tests.quality_tests.utils import predict_with_model

class TestRobustness:
  def test_whitespace_invariance(self, model, tokenizer):
    text = "Renewable energy helps fight climate change."
    text_padded = "  Renewable   energy   helps  fight   climate   change.  "
    
    prob_normal = predict_with_model(model, tokenizer, text, return_details=True)["prob_generated"]
    prob_padded = predict_with_model(model, tokenizer, text_padded, return_details=True)["prob_generated"]
    
    print(f"\nNormal prob: {prob_normal}")
    print(f"Padded prob: {prob_padded}")

    assert abs(prob_normal - prob_padded) < 0.05, "Whitespace significantly affected prediction"

  def test_minor_typo_robustness(self, model, tokenizer):
    text = "Renewable energy helps fight climate change."
    text_typo = "Renewable enrgy helps fight climate change."
    
    prob_normal = predict_with_model(model, tokenizer, text, return_details=True)["prob_generated"]
    prob_typo = predict_with_model(model, tokenizer, text_typo, return_details=True)["prob_generated"]
    
    print(f"Normal prob: {prob_normal}")
    print(f"Typo prob: {prob_typo}")

    label_normal = 1 if prob_normal >= 0.5 else 0
    label_typo = 1 if prob_typo >= 0.5 else 0
    
    assert label_normal == label_typo, "Minor typo flipped the classification label"
