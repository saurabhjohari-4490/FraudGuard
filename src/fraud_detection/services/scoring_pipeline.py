"""Scoring pipeline - registers and executes all scoring modules in parallel."""

import asyncio
import logging

from fraud_detection.scoring.base import ScoringModule, ScoringResult, TransactionContext

logger = logging.getLogger(__name__)


class ScoringPipeline:
    """Orchestrates parallel execution of all scoring modules."""

    def __init__(self) -> None:
        self._modules: list[ScoringModule] = []

    def register(self, module: ScoringModule) -> None:
        """Register a scoring module in the pipeline."""
        self._modules.append(module)
        logger.info(f"Registered scoring module: {module.name} (weight={module.weight})")

    @property
    def modules(self) -> list[ScoringModule]:
        return self._modules

    async def execute(self, context: TransactionContext) -> dict[str, ScoringResult]:
        """Execute all scoring modules in parallel.

        Returns a dict mapping module name -> ScoringResult.
        Failed modules return a neutral score (50) with 0 confidence.
        """
        tasks = [module.score(context) for module in self._modules]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        scores: dict[str, ScoringResult] = {}
        for module, result in zip(self._modules, results):
            if isinstance(result, Exception):
                logger.error(f"Scoring module {module.name} failed: {result}")
                scores[module.name] = ScoringResult(
                    score=50.0,
                    confidence=0.0,
                    signals=[f"Module {module.name} encountered an error"],
                    metadata={"error": str(result)},
                )
            else:
                scores[module.name] = result

        return scores


def create_default_pipeline() -> ScoringPipeline:
    """Create a pipeline with all 6 default scoring modules registered."""
    from fraud_detection.scoring.behavior import BehaviorAnalyzer
    from fraud_detection.scoring.device import DeviceRiskEngine
    from fraud_detection.scoring.geolocation import GeolocationEngine
    from fraud_detection.scoring.ip_intelligence import IPIntelligence
    from fraud_detection.scoring.merchant import MerchantRiskEngine
    from fraud_detection.scoring.velocity import VelocityDetector

    pipeline = ScoringPipeline()
    pipeline.register(BehaviorAnalyzer())
    pipeline.register(VelocityDetector())
    pipeline.register(DeviceRiskEngine())
    pipeline.register(MerchantRiskEngine())
    pipeline.register(GeolocationEngine())
    pipeline.register(IPIntelligence())
    return pipeline
