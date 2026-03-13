from dataclasses import dataclass


@dataclass
class PulseInput:
    worldnews_sentiment: float | None = None  # 0..1
    gdelt_tone: float | None = None  # 0..1
    gdelt_volume: int = 0


@dataclass
class PulseResult:
    composite_score: float
    sentiment_score: float
    conflict_score: float
    trend: str = "stable"


def compute_pulse(inp: PulseInput) -> PulseResult:
    """
    Phase 1 simplified scoring:
    - 70% news sentiment (WorldNews 60% + GDELT 40%)
    - 30% stability (inverse of GDELT volume / baseline)
    """
    # Sentiment component
    sentiment_parts = []
    if inp.worldnews_sentiment is not None:
        sentiment_parts.append((inp.worldnews_sentiment, 0.6))
    if inp.gdelt_tone is not None:
        sentiment_parts.append((inp.gdelt_tone, 0.4))

    if sentiment_parts:
        total_weight = sum(w for _, w in sentiment_parts)
        sentiment_score = sum(v * w for v, w in sentiment_parts) / total_weight
    else:
        sentiment_score = 0.5

    # Conflict component (inverse of GDELT volume, baseline ~20 articles/day)
    baseline_volume = 20
    if inp.gdelt_volume > 0:
        conflict_ratio = min(inp.gdelt_volume / baseline_volume, 5.0) / 5.0
        conflict_score = 1.0 - conflict_ratio * 0.5  # max 50% penalty
    else:
        conflict_score = 0.5

    composite = sentiment_score * 0.7 + conflict_score * 0.3
    composite = max(0.0, min(1.0, composite))

    return PulseResult(
        composite_score=round(composite, 4),
        sentiment_score=round(sentiment_score, 4),
        conflict_score=round(conflict_score, 4),
        trend="stable",
    )
