from unittest import main

from deepeval import assert_test
from deepeval.metrics.g_eval.g_eval import SingleTurnParams

from .llms import OPENAI_REVIEWER_MODEL, prompt_openai
from .tests import StructureTestCase, QualityTestCase


class TestExplainStructure(StructureTestCase):
    EXPLAIN_FULL = StructureTestCase.load_full('agents/Explain.agent.md')
    ASK_FULL = StructureTestCase.load_full('agents/template/Ask.agent.md')

    def test_explain(self) -> None:
        lowered = self.EXPLAIN_FULL.lower()
        self.assertIn('# explain', lowered, 'Explain: missing H1 role heading')
        self.assertIn('never modify files', lowered, 'Explain: missing read-only constraint')
        self.assertIn('never', lowered, 'Explain: missing explicit prohibition ("NEVER ...")')
        self.assertIn('workflow', lowered, 'Explain: missing workflow section')
        self.assertIn('katex', lowered)
        self.assertIn('mermaid', lowered)
        self.assertIn('empathetic', lowered)

    def test_ask(self) -> None:
        lowered = self.ASK_FULL.lower()
        self.assertIn('you are', lowered, 'Ask: missing role definition ("You are ...")')
        self.assertIn('read-only', lowered, 'Ask: missing read-only constraint')
        self.assertIn('never', lowered, 'Ask: missing explicit prohibition ("NEVER ...")')
        self.assertIn('workflow', lowered, 'Ask: missing workflow section')

    def test_explain_has_extra_content(self) -> None:
        self.assertGreater(len(self.EXPLAIN_FULL), len(self.ASK_FULL))


class TestExplainQuality(QualityTestCase):
    EXPLAIN_PROMPT = QualityTestCase.load_prompt('agents/Explain.agent.md')
    ASK_PROMPT = QualityTestCase.load_prompt('agents/template/Ask.agent.md')

    EXPLAIN_METRICS = [
        QualityTestCase.prompt_quality_metric(
            'KaTeX Usage',
            'Does the response render mathematical expressions using KaTeX notation ($...$ ' +
            'or $$...$$) when appropriate?',
            [SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
            model=OPENAI_REVIEWER_MODEL,
        ),
        QualityTestCase.prompt_quality_metric(
            'Mermaid Diagram Usage',
            'Does the response include Mermaid diagram code blocks when describing ' +
            'architecture or workflows?',
            [SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
            model=OPENAI_REVIEWER_MODEL,
        ),
        QualityTestCase.prompt_quality_metric(
            'No Empathetic Language',
            "Does the response avoid complimentary or apologetic language (no 'Great " +
            "question!', 'Sorry about that', etc.)?",
            [SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
            model=OPENAI_REVIEWER_MODEL,
        ),
    ]
    ASK_METRICS = [
        QualityTestCase.prompt_quality_metric(
            'No KaTeX',
            'Does the response avoid using KaTeX notation ($...$ or $$...$$)?',
            [SingleTurnParams.ACTUAL_OUTPUT],
            model=OPENAI_REVIEWER_MODEL,
        ),
        QualityTestCase.prompt_quality_metric(
            'No Mermaid',
            'Does the response avoid including Mermaid diagram code blocks?',
            [SingleTurnParams.ACTUAL_OUTPUT],
            model=OPENAI_REVIEWER_MODEL,
        ),
    ]

    QUESTION = \
        'Explain the architecture of the Flask web framework and describe the flow ' + \
        'of an HTTP request from the WSGI server through to a route handler response.'
    EXTRA_QUESTIONS = [
        'How does Flask handle request routing internally? Explain the WSGI application flow.',
        'What is the difference between React class components and functional components ' +
        'with hooks?',
        'Explain how the Linux kernel manages virtual memory and page tables.',
    ]

    def test_explain_specific_rules(self) -> None:
        case = \
            self.make_test_case(self.QUESTION, prompt_openai(self.EXPLAIN_PROMPT, self.QUESTION))
        for metric in self.EXPLAIN_METRICS:
            assert_test(case, [metric], run_async=False)

    def test_ask_lacks_explain_features(self) -> None:
        case = self.make_test_case(self.QUESTION, prompt_openai(self.ASK_PROMPT, self.QUESTION))
        for metric in self.ASK_METRICS:
            assert_test(case, [metric], run_async=False)

    def test_question1(self) -> None:
        self._assert_responses(self.EXTRA_QUESTIONS[0])

    def test_question2(self) -> None:
        self._assert_responses(self.EXTRA_QUESTIONS[1])

    def test_question3(self) -> None:
        self._assert_responses(self.EXTRA_QUESTIONS[2])

    def _assert_responses(self, question: str) -> None:
        assert_test(
            self.make_test_case(question, prompt_openai(self.EXPLAIN_PROMPT, question)),
            self.METRICS,
            run_async=False,
        )


if __name__ == '__main__':
    main()
