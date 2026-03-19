import pytest, pandas
from pathlib import Path
from sklearn.metrics import accuracy_score, classification_report
from src.nlp.tests.quality_tests.utils import predict_with_model

class TestAccuracy:
  def test_general_correctness(self, model, tokenizer):
    dataset_path = Path(__file__).parent.parent / "resources" / "AI Generated Essays Dataset.csv"
    # dataset_path = Path(__file__).parent.parent / "resources" / "your_dataset_5000.csv"

    if not dataset_path.exists():
      pytest.skip(f"Dataset not found at {dataset_path}")

    df = pandas.read_csv(dataset_path)

    sample_size = 100 #Lepiej testować na jak największej liczbie
    if len(df) > sample_size:
      df_sample = df.sample(n=sample_size, random_state=42)
    else:
      df_sample = df
      
    predictions = []
    true_labels = df_sample['label'].tolist()
    entropies = []
    
    print(f"\nRunning accuracy test on {len(df_sample)} samples...")
    
    for text in df_sample['text']:
      details = predict_with_model(model, tokenizer, text, return_details=True)
      prob = details["prob_generated"]
      pred = 1 if prob >= 0.5 else 0
      predictions.append(pred)
      entropies.append(details["prob_entropy"])
      
    avg_entropy = sum(entropies) / len(entropies)
    print(f"Average Entropy: {avg_entropy:.4f}")
      
    acc = accuracy_score(true_labels, predictions)
    print(f"Accuracy: {acc:.4f}")
    print("\nClassification Report:\n", classification_report(true_labels, predictions))

    assert acc > 0.8, f"Accuracy {acc} is below threshold 0.8"
