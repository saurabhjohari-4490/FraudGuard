"""Unit tests for the scoring pipeline orchestration."""

import pytest
from unittest.mock import AsyncMock

from fraud_detection.scoring.base import ScoringModule, ScoringResult, TransactionContext
from fraud_detection.services.scoring_pipeline import ScoringPipeline, create_default_pipeline


class MockModule(ScoringModule):
    """Test scoring module."""

    name = "mock_module"
    weight = 0.25
    description = "Mock for testing"

    def __init__(self, score: float = 50.0, should_fail: bool = False):
        self._score = score
        self._should_fail = should_fail

    async def score(self, context: TransactionContext) -> ScoringResult:
        if self._should_fail:
            raise RuntimeError("Module failed")
        return ScoringResult(
            score=self._score,
            confidence=0.9,
            signals=[f"Mock signal at {self._score}"],
        )


class TestScoringPipeline:
    @pytest.fixture
    def pipeline(self):
        return ScoringPipeline()

    def test_register_module(self, pipeline):
        """Modules can be registered."""
        module = MockModule(score=30.0)
        pipeline.register(module)
        assert len(pipeline.modules) == 1
        assert pipeline.modules[0].name == "mock_module"

    @pytest.mark.asyncio
    async def test_execute_single_module(self, pipeline, make_scoring_context):
        """Single module execution."""
        pipeline.register(MockModule(score=42.0))
        ctx = make_scoring_context()
        results = await pipeline.execute(ctx)
        assert "mock_module" in results
        assert results["mock_module"].score == 42.0

    @pytest.mark.asyncio
    async def test_execute_parallel(self, pipeline, make_scoring_context):
        """Multiple modules execute in parallel."""
        m1 = MockModule(score=20.0)
        m1.name = "module_a"
        m2 = MockModule(score=60.0)
        m2.name = "module_b"
        m3 = MockModule(score=80.0)
        m3.name = "module_c"

        pipeline.register(m1)
        pipeline.register(m2)
        pipeline.register(m3)

        ctx = make_scoring_context()
        results = await pipeline.execute(ctx)

        assert len(results) == 3
        assert results["module_a"].score == 20.0
        assert results["module_b"].score == 60.0
        assert results["module_c"].score == 80.0

    @pytest.mark.asyncio
    async def test_failed_module_graceful_degradation(self, pipeline, make_scoring_context):
        """Failed module gets neutral score with 0 confidence."""
        good = MockModule(score=30.0)
        good.name = "good_module"
        bad = MockModule(should_fail=True)
        bad.name = "bad_module"

        pipeline.register(good)
        pipeline.register(bad)

        ctx = make_scoring_context()
        results = await pipeline.execute(ctx)

        assert results["good_module"].score == 30.0
        assert results["bad_module"].score == 50.0
        assert results["bad_module"].confidence == 0.0
        assert "error" in (results["bad_module"].metadata or {})

    @pytest.mark.asyncio
    async def test_empty_pipeline(self, pipeline, make_scoring_context):
        """Empty pipeline returns empty results."""
        ctx = make_scoring_context()
        results = await pipeline.execute(ctx)
        assert results == {}


class TestCreateDefaultPipeline:
    def test_has_six_modules(self):
        """Default pipeline should have all 6 scoring modules."""
        pipeline = create_default_pipeline()
        assert len(pipeline.modules) == 6

    def test_weights_sum_to_one(self):
        """Module weights should sum to 1.0."""
        pipeline = create_default_pipeline()
        total_weight = sum(m.weight for m in pipeline.modules)
        assert total_weight == pytest.approx(1.0)

    def test_module_names(self):
        """All expected module names are present."""
        pipeline = create_default_pipeline()
        names = {m.name for m in pipeline.modules}
        expected = {"behavior", "velocity", "device_risk", "merchant_risk", "geolocation", "ip_intelligence"}
        assert names == expected
