from transformers import AutoTokenizer, AutoModelForSequenceClassification

def load_roberta_model():
  model_name="roberta-base-openai-detector"
  tokenizer= AutoTokenizer.from_pretrained(model_name)
  model= AutoModelForSequenceClassification.from_pretrained(model_name)
  return tokenizer, model

