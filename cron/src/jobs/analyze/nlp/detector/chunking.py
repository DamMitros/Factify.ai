import re
from dataclasses import dataclass
from typing import Iterable, List

@dataclass(frozen=True, slots=True)
class WordSpan:
	index: int
	start: int
	end: int
	is_sentence_end: bool

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
_SENTENCE_END_PATTERN = re.compile(r'[.!?]+["\')\]]*$')

def iter_word_spans(text: str) -> Iterable[WordSpan]:
	for idx, match in enumerate(_WORD_PATTERN.finditer(text)):
		word_text = match.group()
		is_end = bool(_SENTENCE_END_PATTERN.search(word_text))
		yield WordSpan(index=idx, start=match.start(), end=match.end(), is_sentence_end=is_end)

def find_nearest_sentence_boundary(spans: List[WordSpan], target_idx: int, 
	min_idx: int, max_idx: int) -> int:
	best_idx = -1
	min_dist = float('inf')

	search_start = max(min_idx, 0)
	search_end = min(max_idx, len(spans))

	for i in range(search_start, search_end):
		if spans[i].is_sentence_end:
			cut_point = i + 1
			dist = abs(cut_point - target_idx)
			if dist < min_dist:
				min_dist = dist
				best_idx = cut_point
			elif dist == min_dist:
				best_idx = max(best_idx, cut_point)
	
	return best_idx if best_idx != -1 else target_idx

def build_chunks(text: str, *, words_per_chunk: int, stride_words: int | None = None,
	min_words: int = 1) -> List[TextChunk]:
	
	if words_per_chunk <= 0:
		raise ValueError("words_per_chunk must be positive")

	resolved_stride = stride_words if stride_words is not None else words_per_chunk
	resolved_stride = max(1, resolved_stride)

	spans = list(iter_word_spans(text))
	total_words = len(spans)
	
	if not spans:
		return []

	chunks: List[TextChunk] = []
	current_word_idx = 0
	chunk_index = 0
	
	search_window = max(3, int(words_per_chunk * 0.25)) 

	while current_word_idx < total_words:
		target_end = current_word_idx + words_per_chunk
		words_remaining_after = total_words - target_end
		tail_threshold = max(min_words, int(words_per_chunk * 0.5)) # procent "toleracji" długości ostatniego chunka
		
		if words_remaining_after < tail_threshold and words_remaining_after > 0:
			target_end = total_words
			search_window_start = target_end - search_window 
			search_window_end = total_words
		else:
			search_window_start = target_end - search_window
			search_window_end = target_end + search_window

		safe_min_idx = current_word_idx + min_words
		actual_min_search = max(safe_min_idx, search_window_start)
		
		cut_idx = find_nearest_sentence_boundary(
			spans, 
			target_idx=target_end, 
			min_idx=actual_min_search, 
			max_idx=search_window_end
		)

		cut_idx = min(cut_idx, total_words)
		if cut_idx <= current_word_idx:
			cut_idx = min(current_word_idx + words_per_chunk, total_words)

		start_char = spans[current_word_idx].start
		end_char = spans[cut_idx - 1].end
		chunk_text = text[start_char:end_char]

		chunks.append(TextChunk(
			index=chunk_index,
			start=start_char,
			end=end_char,
			text=chunk_text,
			word_start=current_word_idx,
			word_end=cut_idx,
			word_count=cut_idx - current_word_idx
		))
		chunk_index += 1

		if cut_idx >= total_words:
			break

		next_target_start = current_word_idx + resolved_stride
		if resolved_stride < words_per_chunk:
			smart_next_start = find_nearest_sentence_boundary(
				spans,
				target_idx=next_target_start,
				min_idx=current_word_idx + 1, 
				max_idx=next_target_start + search_window
			)
			current_word_idx = smart_next_start
		else:
			current_word_idx = cut_idx

	return chunks