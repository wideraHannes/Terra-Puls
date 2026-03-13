"""
INTENTIONAL FAILURE DEMONSTRATIONS for test/scoring-engine branch.

These tests WILL FAIL — that is their purpose. They demonstrate that
our test suite catches wrong values and is not trivially passing.

Run with: pytest tests/test_FAIL_demo_scoring.py -v
Expected: ALL tests in this file FAIL
"""
import pytest
from app.scoring.pulse_engine import PulseInput, compute_pulse


class TestIntentionalFailures:
    """These tests assert WRONG expected values to prove tests are failable."""

    def test_FAILS_wrong_neutral_composite(self):
        """WILL FAIL: neutral composite is 0.5, not 0.9."""
        result = compute_pulse(PulseInput())
        assert result.composite_score == pytest.approx(0.9, abs=1e-4), (
            "DEMO FAILURE: neutral composite should be 0.5, not 0.9. "
            f"Actual: {result.composite_score}"
        )

    def test_FAILS_wrong_weighting_assumption(self):
        """WILL FAIL: 60/40 weighting means result is 0.6, not 0.5."""
        result = compute_pulse(PulseInput(worldnews_sentiment=1.0, gdelt_tone=0.0))
        assert result.sentiment_score == pytest.approx(0.5, abs=1e-4), (
            "DEMO FAILURE: weighted average with worldnews=1.0, gdelt=0.0 is 0.6 (60% weight), not 0.5. "
            f"Actual: {result.sentiment_score}"
        )

    def test_FAILS_conflict_wrong_formula(self):
        """WILL FAIL: volume=20 gives conflict=0.9, not 1.0."""
        result = compute_pulse(PulseInput(gdelt_volume=20))
        assert result.conflict_score == pytest.approx(1.0, abs=1e-4), (
            "DEMO FAILURE: baseline volume (20) gives 0.9 conflict, not 1.0. "
            f"Actual: {result.conflict_score}"
        )

    def test_FAILS_composite_wrong_weights(self):
        """WILL FAIL: composite = 0.85, not 1.0."""
        result = compute_pulse(PulseInput(worldnews_sentiment=1.0))
        assert result.composite_score == pytest.approx(1.0, abs=1e-4), (
            "DEMO FAILURE: sentiment=1.0, conflict=0.5 → composite = 0.85, not 1.0. "
            f"Actual: {result.composite_score}"
        )
