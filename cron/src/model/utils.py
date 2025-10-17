import re 
from transformers import AutoTokenizer

def preprocess_text(text: str, tokenizer: str="roberta-base") -> dict:
  text=re.sub(r"\s+", " ", text).strip()
  text=re.sub(r'[^\w\s]', '', text)

  tokenizer=AutoTokenizer.from_pretrained(tokenizer)
  inputs=tokenizer(text, truncation=True, padding='max_length', max_length=512)
  return inputs

def calculate_accuracy(predictions, labels):
  correct = (predictions == labels).sum().item()
  return correct / len(labels)