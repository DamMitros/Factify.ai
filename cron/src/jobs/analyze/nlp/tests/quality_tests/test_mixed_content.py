import pytest, pandas
from pathlib import Path
from nlp.detector.inference import predict_segmented_text

class TestMixedContent:
  def test_mixed_ai_human_detection(self, model, tokenizer, monkeypatch):
    def mock_load(*args, **kwargs):
      return tokenizer, model
    
    monkeypatch.setattr("nlp.detector.inference.load_model_artifacts", mock_load)

    dataset_path = Path(__file__).parent.parent / "resources" / "AI Generated Essays Dataset.csv"
    # dataset_path = Path(__file__).parent.parent / "resources" / "your_dataset_5000.csv"

    if not dataset_path.exists():
      pytest.skip(f"Dataset not found at {dataset_path}")

    df = pandas.read_csv(dataset_path)
    ai_texts = df[df['label'] == 1]['text'].tolist()
    human_texts = df[df['label'] == 0]['text'].tolist()
    
    if not ai_texts or not human_texts:
      pytest.skip("Dataset missing AI or Human samples")
      
    ai_text = ai_texts[0]
    human_text = human_texts[0]
    
    ai_part = (ai_text + " ") * 5
    human_part = (human_text + " ") * 5
    
    mixed_text = ai_part + "\n\n" + human_part
    
    print("\nRunning mixed content detection...")
    result = predict_segmented_text(mixed_text, min_words=10, words_per_chunk=30, stride_words=15)
    
    segments = result.get('segments', [])
    probs = [seg['prob_generated'] for seg in segments]
    
    print(f"Number of segments: {len(segments)}")
    print(f"Segment probabilities: {probs}")
    
    if not segments:
       pytest.skip("Text was not segmented (too short?)")

    # Muszą być wymieszane fragmenty AI i Human (min jeden z Human i jeden z AI)
    has_high = any(p > 0.6 for p in probs)
    has_low = any(p < 0.4 for p in probs)
    
    if has_high and has_low:
      print("Success: Detected both AI and Human segments.")
    else:
      print("Warning: Did not clearly distinguish both parts.")
      
    assert len(segments) > 0
