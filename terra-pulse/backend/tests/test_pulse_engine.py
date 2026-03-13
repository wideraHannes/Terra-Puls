"""Tests for app/scoring/pulse_engine.py — all tests are failable (assert real computed values)."""
import pytest
from app.scoring.pulse_engine import PulseInput, compute_pulse, PulseResult


class TestComputePulseNeutral:
    """Baseline: no inputs → neutral 0.5 scores."""

    def test_no_inputs_composite_is_neutral(self):
        result = compute_pulse(PulseInput())
        assert result.composite_score == pytest.approx(0.5, abs=1e-4)

    def test_no_inputs_sentiment_is_neutral(self):
        result = compute_pulse(PulseInput())
        assert result.sentiment_score == pytest.approx(0.5, abs=1e-4)

    def test_no_inputs_conflict_is_neutral(self):
        result = compute_pulse(PulseInput())
        assert result.conflict_score == pytest.approx(0.5, abs=1e-4)

    def test_no_inputs_trend_is_stable(self):
        result = compute_pulse(PulseInput())
        assert result.trend == "stable"

    def test_returns_pulse_result_type(self):
        result = compute_pulse(PulseInput())
        assert isinstance(result, PulseResult)


class TestSentimentWeighting:
    """Sentiment: WorldNews 60% + GDELT 40% weighted average."""

    def test_only_worldnews_sentiment_used_when_gdelt_absent(self):
        # Only worldnews → sentiment = worldnews_sentiment (weight normalises to 1.0)
        result = compute_pulse(PulseInput(worldnews_sentiment=0.8))
        assert result.sentiment_score == pytest.approx(0.8, abs=1e-4)

    def test_only_gdelt_tone_used_when_worldnews_absent(self):
        # Only gdelt → sentiment = gdelt_tone (weight normalises to 1.0)
        result = compute_pulse(PulseInput(gdelt_tone=0.3))
        assert result.sentiment_score == pytest.approx(0.3, abs=1e-4)

    def test_both_sources_weighted_60_40(self):
        # worldnews=1.0 (w=0.6), gdelt=0.0 (w=0.4) → (1.0*0.6 + 0.0*0.4) / 1.0 = 0.6
        result = compute_pulse(PulseInput(worldnews_sentiment=1.0, gdelt_tone=0.0))
        assert result.sentiment_score == pytest.approx(0.6, abs=1e-4)

    def test_both_sources_equal_value(self):
        # worldnews=0.5, gdelt=0.5 → 0.5 regardless of weighting
        result = compute_pulse(PulseInput(worldnews_sentiment=0.5, gdelt_tone=0.5))
        assert result.sentiment_score == pytest.approx(0.5, abs=1e-4)

    def test_worldnews_has_more_weight_than_gdelt(self):
        # worldnews=1.0 (w=0.6) vs gdelt=0.0 (w=0.4): score should be 0.6, skewed toward worldnews
        result_wn_high = compute_pulse(PulseInput(worldnews_sentiment=1.0, gdelt_tone=0.0))
        result_gdelt_high = compute_pulse(PulseInput(worldnews_sentiment=0.0, gdelt_tone=1.0))
        assert result_wn_high.sentiment_score > result_gdelt_high.sentiment_score


class TestConflictScore:
    """Conflict score: inverse of GDELT volume, baseline=20, max 50% penalty."""

    def test_zero_volume_gives_neutral_conflict(self):
        result = compute_pulse(PulseInput(gdelt_volume=0))
        assert result.conflict_score == pytest.approx(0.5, abs=1e-4)

    def test_baseline_volume_gives_half_penalty(self):
        # volume=20 (=baseline): ratio=1.0/5.0=0.2, conflict = 1.0 - 0.2*0.5 = 0.9
        result = compute_pulse(PulseInput(gdelt_volume=20))
        assert result.conflict_score == pytest.approx(0.9, abs=1e-4)

    def test_max_volume_caps_at_0_5_penalty(self):
        # volume=100 (5x baseline): ratio=5/5=1.0, conflict = 1.0 - 1.0*0.5 = 0.5
        result = compute_pulse(PulseInput(gdelt_volume=100))
        assert result.conflict_score == pytest.approx(0.5, abs=1e-4)

    def test_very_high_volume_capped(self):
        # volume=999 (>5x baseline): should be capped same as volume=100
        result_high = compute_pulse(PulseInput(gdelt_volume=999))
        result_cap = compute_pulse(PulseInput(gdelt_volume=100))
        assert result_high.conflict_score == result_cap.conflict_score

    def test_low_volume_close_to_1(self):
        # volume=1 (very low): ratio = (1/20)/5 = 0.01, conflict = 1 - 0.01*0.5 = 0.995
        result = compute_pulse(PulseInput(gdelt_volume=1))
        assert result.conflict_score == pytest.approx(0.995, abs=1e-4)

    def test_high_volume_reduces_conflict_score(self):
        low_vol = compute_pulse(PulseInput(gdelt_volume=5))
        high_vol = compute_pulse(PulseInput(gdelt_volume=50))
        assert low_vol.conflict_score > high_vol.conflict_score


class TestCompositeFormula:
    """Composite = sentiment*0.7 + conflict*0.3, clamped to [0,1]."""

    def test_composite_formula_explicit(self):
        # worldnews=1.0 only → sentiment=1.0; volume=0 → conflict=0.5
        # composite = 1.0*0.7 + 0.5*0.3 = 0.7 + 0.15 = 0.85
        result = compute_pulse(PulseInput(worldnews_sentiment=1.0, gdelt_volume=0))
        assert result.composite_score == pytest.approx(0.85, abs=1e-4)

    def test_composite_clamped_to_max_1(self):
        # max sentiment=1.0, max conflict=1.0 → composite = 1.0*0.7 + 1.0*0.3 = 1.0
        result = compute_pulse(PulseInput(worldnews_sentiment=1.0, gdelt_tone=1.0))
        assert result.composite_score <= 1.0

    def test_composite_clamped_to_min_0(self):
        # min sentiment=0.0, min conflict (volume=0 so 0.5) → composite = 0.0*0.7 + 0.5*0.3 = 0.15
        result = compute_pulse(PulseInput(worldnews_sentiment=0.0, gdelt_tone=0.0))
        assert result.composite_score >= 0.0

    def test_composite_in_valid_range(self):
        for sentiment in [0.0, 0.25, 0.5, 0.75, 1.0]:
            for volume in [0, 10, 20, 100]:
                result = compute_pulse(PulseInput(worldnews_sentiment=sentiment, gdelt_volume=volume))
                assert 0.0 <= result.composite_score <= 1.0

    def test_scores_rounded_to_4_decimal_places(self):
        result = compute_pulse(PulseInput(worldnews_sentiment=0.333333, gdelt_tone=0.666666))
        # Values should be rounded to 4 decimal places (no more than 4 decimals)
        assert result.composite_score == round(result.composite_score, 4)
        assert result.sentiment_score == round(result.sentiment_score, 4)
        assert result.conflict_score == round(result.conflict_score, 4)
