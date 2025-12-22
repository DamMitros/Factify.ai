import pytest
from src.nlp.tests.quality_tests.utils import predict_with_model

class TestConsistency:
  def test_repetitiveness(self, model, tokenizer):
    text = "Renewable energy helps fight climate change by reducing the amount of greenhouse gases released into the atmosphere."
    
    results = []
    entropies = []
    print("\nRunning consistency test (5 iterations)...")
    for i in range(5):
      details = predict_with_model(model, tokenizer, text, return_details=True)
      prob = details["prob_generated"]
      entropy = details["prob_entropy"]
      results.append(prob)
      entropies.append(entropy)
      print(f"Iteration {i+1}: Prob={prob}, Entropy={entropy}")
      
    first_res = results[0]
    first_ent = entropies[0]
    for res, ent in zip(results[1:], entropies[1:]):
      assert abs(res - first_res) < 1e-6, f"Inconsistent probabilities: {results}"
      assert abs(ent - first_ent) < 1e-6, f"Inconsistent entropy: {entropies}"
