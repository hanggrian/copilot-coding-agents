from unittest import TestCase

from deepeval.metrics import GEval, AnswerRelevancyMetric, BaseMetric
from deepeval.models import DeepEvalBaseLLM
from deepeval.test_case import SingleTurnParams, LLMTestCase

from tests.llms import OPENAI_REVIEWER_MODEL


class StructureTestCase(TestCase):
    @staticmethod
    def load_full(path: str) -> str:
        with open(path, encoding='UTF-8') as fh:
            return fh.read().strip()


class QualityTestCase(TestCase):
    METRICS: list[BaseMetric] = [
        AnswerRelevancyMetric(
            threshold=0.5,
            model=OPENAI_REVIEWER_MODEL,
            include_reason=True,
        ),
    ]

    @staticmethod
    def prompt_quality_metric(
        name: str,
        criteria: str,
        evaluation_params: list[SingleTurnParams] | None = None,
        model: str | DeepEvalBaseLLM | None = None,
    ) -> GEval:
        return GEval(
            name=name,
            criteria=criteria,
            evaluation_params=evaluation_params or [SingleTurnParams.ACTUAL_OUTPUT],
            threshold=0.5,
            model=model,
        )

    @staticmethod
    def make_test_case(
        question: str,
        actual: str | None,
        expected: str = '',
        context: list[str] | None = None,
    ) -> LLMTestCase:
        if actual is None:
            raise ValueError('LLM returned an empty response.')
        return LLMTestCase(
            input=question,
            actual_output=actual,
            expected_output=expected,
            context=context or [],
        )

    @staticmethod
    def load_prompt(path: str) -> str:
        with open(path, encoding='UTF-8') as fh:
            text = fh.read()
        if text.startswith('---'):
            parts = text.split('---', 2)
            if len(parts) >= 3:
                text = parts[2]
        return text.strip()
