from typing import Sequence

import pandas as pd

def compute_dataset_stats(train_frame: pd.DataFrame, test_frame: pd.DataFrame) -> dict[str, object]:
	def describe(frame: pd.DataFrame) -> dict[str, object]:
		lengths = frame["text"].astype(str).str.split().apply(len)
		class_counts = frame["generated"].value_counts().sort_index()
		return {
			"samples": int(len(frame)),
			"class_counts": {int(k): int(v) for k, v in class_counts.items()},
			"mean_word_count": float(lengths.mean()) if not lengths.empty else 0.0,
			"median_word_count": float(lengths.median()) if not lengths.empty else 0.0,
			"std_word_count": float(lengths.std(ddof=0)) if len(lengths) > 1 else 0.0,
			"min_word_count": int(lengths.min()) if not lengths.empty else 0,
			"max_word_count": int(lengths.max()) if not lengths.empty else 0,
		}

	global_frame = pd.concat([train_frame, test_frame], ignore_index=True)
	return {
		"train": describe(train_frame),
		"test": describe(test_frame),
		"full": describe(global_frame),
	}

def compute_length_bucket_metrics(records: Sequence[dict[str, float | int | str]], *, bucket_edges: Sequence[int] = (0, 150, 300, 600, 1200)) -> dict[str, object]:
	buckets: dict[str, dict[str, object]] = {}
	if not records:
		return buckets

	def resolve_bucket(length: int) -> str:
		for left, right in zip(bucket_edges[:-1], bucket_edges[1:]):
			if left <= length < right:
				return f"{left}-{right - 1}"
		return f">={bucket_edges[-1]}"

	for record in records:
		length = record.get("word_count")
		if length is None:
			continue
		bucket_name = resolve_bucket(int(length))
		bucket_stats = buckets.setdefault(bucket_name, {"samples": 0, "correct": 0, "incorrect": 0})
		bucket_stats["samples"] += 1
		if record.get("true_label") == record.get("pred_label"):
			bucket_stats["correct"] += 1
		else:
			bucket_stats["incorrect"] += 1

	for bucket_stats in buckets.values():
		samples = bucket_stats["samples"] or 1
		bucket_stats["accuracy"] = bucket_stats["correct"] / samples
