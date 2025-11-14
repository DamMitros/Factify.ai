import re
from dataclasses import dataclass
from typing import Iterable, List

@dataclass(frozen=True, slots=True)
class WordSpan:
	index: int
	start: int
	end: int

@dataclass(frozen=True, slots=True)
class TextChunk:
	index: int
	start: int
	end: int
	text: str
	word_start: int
	word_end: int
	word_count: int

_WORD_PATTERN = re.compile(r"\S+")

def iter_word_spans(text: str) -> Iterable[WordSpan]:
	for idx, match in enumerate(_WORD_PATTERN.finditer(text)):
		yield WordSpan(index=idx, start=match.start(), end=match.end())

def build_chunks(text: str, *, words_per_chunk: int, stride_words: int | None = None,
								 min_words: int = 1) -> List[TextChunk]:
	
	if words_per_chunk <= 0:
		raise ValueError("words_per_chunk must be positive")
	if stride_words is not None and stride_words <= 0:
		raise ValueError("stride_words must be positive if provided")
	if min_words < 1:
		raise ValueError("min_words must be at least 1")

	spans = list(iter_word_spans(text))
	if not spans:
		return []

	resolved_stride = stride_words if stride_words is not None else words_per_chunk
	resolved_stride = max(1, resolved_stride)
	resolved_stride = min(resolved_stride, words_per_chunk)
	target = max(1, words_per_chunk)
	minimum = max(1, min_words)

	chunks: List[TextChunk] = []
	word_start_idx = 0
	chunk_index = 0
	total_words = len(spans)

	while word_start_idx < total_words:
		word_end_idx = min(word_start_idx + target, total_words)
		if word_end_idx - word_start_idx < minimum and word_end_idx < total_words:
			word_end_idx = min(word_start_idx + minimum, total_words)

		start_char = spans[word_start_idx].start
		end_char = spans[word_end_idx - 1].end
		chunk_text = text[start_char:end_char]

		chunks.append(TextChunk(
			index=chunk_index,
			start=start_char,
			end=end_char,
			text=chunk_text,
			word_start=word_start_idx,
			word_end=word_end_idx,
			word_count=word_end_idx - word_start_idx
		))

		chunk_index += 1
		if word_end_idx >= total_words:
			break
		word_start_idx = min(word_start_idx + resolved_stride, total_words)

	last_chunk = chunks[-1]
	if last_chunk.word_end < total_words:
		start_span = spans[last_chunk.word_end]
		chunks.append(TextChunk(
			index=chunk_index,
			start=start_span.start,
			end=spans[-1].end,
			text=text[start_span.start:spans[-1].end],
			word_start=start_span.index,
			word_end=total_words,
			word_count=total_words - start_span.index
		))

	return chunks
