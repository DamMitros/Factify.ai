from pathlib import Path
from typing import Dict, Optional, Tuple

import pandas as pd, torch
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Dataset
from transformers import AutoTokenizer

class EssayDataset(Dataset):
	def __init__(self, frame: pd.DataFrame, tokenizer: AutoTokenizer, max_length: int = 512) -> None:
		self.frame = frame.reset_index(drop=True)
		self.tokenizer = tokenizer
		self.max_length = max_length

	def __len__(self) -> int:
		return len(self.frame)

	def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
		row = self.frame.iloc[idx]
		encoding = self.tokenizer(
			str(row["text"]),
			truncation=True,
			padding="max_length",
			max_length=self.max_length,
			return_tensors="pt"
		)
		item = {key: value.squeeze(0) for key, value in encoding.items()}
		item["labels"] = torch.tensor(int(row["generated"]), dtype=torch.long)
		item["sample_id"] = torch.tensor(idx, dtype=torch.long)
		return item

def prepare_splits(
	data_path: Path | str,
	*,
	test_size: float,
	calibration_size: float,
	random_state: int
) -> Tuple[pd.DataFrame, Optional[pd.DataFrame], pd.DataFrame]:
	if not 0 < test_size < 1:
		raise ValueError("test_size must be between 0 and 1")
	if not 0 <= calibration_size < 1:
		raise ValueError("calibration_size must be between 0 (inclusive) and 1 (exclusive)")

	frame = pd.read_csv(data_path)
	frame = frame.dropna(subset=["text", "generated"]).copy()
	frame["generated"] = frame["generated"].astype(int)

	train_frame, test_frame = train_test_split(
		frame,
		test_size=test_size,
		stratify=frame["generated"],
		random_state=random_state
	)

	calibration_frame: Optional[pd.DataFrame] = None
	if calibration_size > 0:
		train_frame, calibration_frame = train_test_split(
			train_frame,
			test_size=calibration_size,
			stratify=train_frame["generated"],
			random_state=random_state
		)

	return train_frame, calibration_frame, test_frame

def create_dataloaders(
	train_frame: pd.DataFrame,
	calibration_frame: Optional[pd.DataFrame],
	test_frame: pd.DataFrame,
	tokenizer: AutoTokenizer,
	*,
	max_length: int,
	batch_size: int
) -> Tuple[DataLoader, Optional[DataLoader], DataLoader]:
	train_dataset = EssayDataset(train_frame, tokenizer, max_length=max_length)
	train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

	calibration_loader: Optional[DataLoader] = None
	if calibration_frame is not None and not calibration_frame.empty:
		calibration_dataset = EssayDataset(calibration_frame, tokenizer, max_length=max_length)
		calibration_loader = DataLoader(calibration_dataset, batch_size=batch_size, shuffle=False)

	test_dataset = EssayDataset(test_frame, tokenizer, max_length=max_length)
	test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

	return train_loader, calibration_loader, test_loader
