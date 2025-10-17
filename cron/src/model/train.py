import pandas as pd, torch
from torch.utils.data import DataLoader, Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, DataCollatorWithPadding

from utils import preprocess_text

class TextDataset(Dataset):
  def __init__(self, csv_file, tokenizer_name="roberta-base"):
    self.data=pd.read_csv(csv_file)
    self.tokenizer_name=tokenizer_name

  def __len__(self):
    return len(self.data)
  
  def __getitem__(self, idx):
    text=self.data.iloc[idx]["text"]
    label=self.data.iloc[idx]["label"]
    inputs=preprocess_text(text, self.tokenizer_name)
    inputs["labels"]=torch.tensor(label, dtype=torch.long)
    return inputs
  
def train_model(csv_file, epochs=3, lr=1e-5):
  tokenizer_name="roberta-base"
  tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
  model = AutoModelForSequenceClassification.from_pretrained(tokenizer_name, num_labels=2)
  optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
  loss_fn = torch.nn.CrossEntropyLoss()

  dataset = TextDataset(csv_file, tokenizer_name)
  data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
  dataloader = DataLoader(dataset, batch_size=4, shuffle=True, collate_fn=data_collator)

  model.train()
  for epoch in range(epochs):
    total_loss = 0
    for batch in dataloader:
      optimizer.zero_grad()
      outputs = model(**{k: v for k, v in batch.items() if k != "labels"})
      loss = loss_fn(outputs.logits, batch["labels"])
      loss.backward()
      optimizer.step()
      total_loss += loss.item()
    avg_loss = total_loss / len(dataloader)
    print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")

  torch.save(model.state_dict(), 'cron/src/model/trained_models/roberta_{epochs}.pt'.format(epochs=epochs))
  print("Model zakończył trening. Zapisany w 'cron/src/model/trained_models/'")

if __name__ == "__main__":
  train_model('cron/src/model/data/train.csv', epochs=10)

  