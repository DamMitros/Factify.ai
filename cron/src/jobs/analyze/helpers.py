from .nlp import predict_segmented_text
from .nlp.detector.config import SEGMENT_MIN_WORDS, SEGMENT_STRIDE_WORDS, SEGMENT_WORD_TARGET


def helper_to_predict(text, segment_params):
    words_per_chunk = int(segment_params.get("words_per_chunk", SEGMENT_WORD_TARGET))
    stride_words = segment_params.get("stride_words", SEGMENT_STRIDE_WORDS)

    if stride_words is not None:
        stride_words = int(stride_words)

    min_words = int(segment_params.get("min_words", SEGMENT_MIN_WORDS))
    max_length = int(segment_params.get("max_length", 128))

    segmented = predict_segmented_text(
        text,
        words_per_chunk=words_per_chunk,
        stride_words=stride_words,
        min_words=min_words,
        max_length=max_length,
    )
    overall = segmented["overall"]
    ai_prob = overall["prob_generated"]
    human_prob = overall["prob_human"]
    details = {
        "prob_generated": overall["prob_generated"],
        "prob_generated_std": overall.get("prob_generated_std", 0.0),
        "prob_human": overall["prob_human"],
        "prob_human_std": overall.get("prob_human_std", 0.0),
        "prob_generated_raw": overall.get("prob_generated_raw", overall["prob_generated"]),
        "prob_human_raw": overall.get("prob_human_raw", overall["prob_human"]),
        "prob_entropy": overall.get("prob_entropy"),
        "prob_variation_ratio": overall.get("prob_variation_ratio"),
        "mc_dropout_passes": segmented.get("mc_dropout_passes"),
        "temperature": segmented.get("temperature"),
    }

    ai_prob_pct = round(ai_prob * 100, 2)
    human_prob_pct = round(human_prob * 100, 2)
    response = {
        "text": text,
        "ai_probability": ai_prob_pct,
        "human_probability": human_prob_pct,
        "details": details,
        "overall": segmented["overall"],
        "segments": segmented["segments"],
        "segment_params": segmented["params"],
        "mc_dropout_passes": segmented.get("mc_dropout_passes"),
        "temperature": segmented.get("temperature")
    }

    if segmented.get("mc_dropout_passes") and segmented["mc_dropout_passes"] > 1:
        response["ai_probability_std"] = round(overall.get("prob_generated_std", 0.0) * 100, 2)
        response["human_probability_std"] = round(overall.get("prob_human_std", 0.0) * 100, 2)
        response["uncertainty_entropy"] = overall.get("prob_entropy")
        response["uncertainty_variation_ratio"] = overall.get("prob_variation_ratio")

    return response, ai_prob_pct
