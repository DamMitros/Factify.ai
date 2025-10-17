import torch
from model.roberta_model import load_roberta_model

tokenizer, model = load_roberta_model()

def predict(text: str) -> float:
  inputs=tokenizer(text, return_tensors="pt", truncation=True, padding=True)
  with torch.no_grad():
    outputs=model(**inputs)
    logits=outputs.logits
    probs=torch.softmax(logits, dim=1)
    ai_prob=probs[0][1].item()
  return round(ai_prob*100, 2)