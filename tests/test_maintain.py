from unittest import main

from deepeval import assert_test
from deepeval.metrics.g_eval.g_eval import SingleTurnParams

from .llms import OPENAI_REVIEWER_MODEL, prompt_openai
from .tests import StructureTestCase, QualityTestCase


class TestMaintainStructure(StructureTestCase):
    MAINTAIN_FULL = StructureTestCase.load_full('agents/Maintain.agent.md')
    ACCESSIBILITY_FULL = \
        StructureTestCase.load_full('template/accessibility-runtime-tester.agent.md')

    def test_maintain(self) -> None:
        lowered = self.MAINTAIN_FULL.lower()
        self.assertIn('# maintain', lowered, 'Maintain: missing H1 role heading')
        self.assertIn('use file editing tools', lowered, 'Maintain: missing write capability')
        self.assertIn('never', lowered, 'Maintain: missing explicit prohibition ("NEVER ...")')
        self.assertIn('workflow', lowered, 'Maintain: missing workflow section')
        self.assertIn('empathetic', lowered)
        self.assertIn('evidence-based', lowered)

    def test_accessibility(self) -> None:
        lowered = self.ACCESSIBILITY_FULL.lower()
        self.assertIn(
            '# accessibility runtime tester',
            lowered,
            'Accessibility: missing H1 role heading',
        )
        self.assertIn(
            'you are',
            lowered,
            'Accessibility: missing role definition ("You are ...")',
        )
        self.assertIn('keyboard', lowered, 'Accessibility: missing keyboard navigation concept')
        self.assertIn('focus', lowered, 'Accessibility: missing focus management concept')
        self.assertIn('wcag', lowered, 'Accessibility: missing WCAG reference')
        self.assertIn(
            'investigation workflow',
            lowered,
            'Accessibility: missing investigation workflow section',
        )
        self.assertIn('constraints', lowered, 'Accessibility: missing constraints section')
        self.assertIn(
            'do not',
            lowered,
            'Accessibility: missing explicit prohibition ("Do not ...")',
        )

    def test_maintain_vs_accessibility_length(self) -> None:
        self.assertGreater(len(self.ACCESSIBILITY_FULL), len(self.MAINTAIN_FULL))


class TestMaintainQuality(QualityTestCase):
    MAINTAIN_PROMPT = QualityTestCase.load_prompt('agents/Maintain.agent.md')

    MAINTAIN_METRICS = [
        QualityTestCase.prompt_quality_metric(
            'Iterative Fixes',
            'Does the response recommend fixing issues one at a time and checking for ' +
            'regression after each change, rather than bundling all fixes together?',
            [SingleTurnParams.ACTUAL_OUTPUT],
            model=OPENAI_REVIEWER_MODEL,
        ),
        QualityTestCase.prompt_quality_metric(
            'No Clarification Requests',
            'Does the response avoid asking for clarification about the error? The answer ' +
            'should diagnose and fix based on available information without requesting more ' +
            'details from the user.',
            [SingleTurnParams.ACTUAL_OUTPUT],
            model=OPENAI_REVIEWER_MODEL,
        ),
        QualityTestCase.prompt_quality_metric(
            'No Empathetic Language',
            "Does the response avoid complimentary or apologetic language (no 'Great question!', "
            "'Sorry about that', etc.)?",
            [SingleTurnParams.ACTUAL_OUTPUT],
            model=OPENAI_REVIEWER_MODEL,
        ),
    ]

    QUESTION = \
        'A Python test is failing with "AssertionError: expected 5 but got 3". How would you ' + \
        'fix this?'
    EXTRA_QUESTIONS = [
        'The linter reports an unused import on line 12. What steps do you take to resolve this?',
        'A CI pipeline failed because of a type annotation mismatch. How do you debug and fix '
        'the issue?',
    ]

    def test_maintain_specific_rules(self) -> None:
        case = \
            self.make_test_case(self.QUESTION, prompt_openai(self.MAINTAIN_PROMPT, self.QUESTION))
        for metric in self.MAINTAIN_METRICS:
            assert_test(case, [metric], run_async=False)

    def test_question1(self) -> None:
        self._assert_responses(self.EXTRA_QUESTIONS[0])

    def test_question2(self) -> None:
        self._assert_responses(self.EXTRA_QUESTIONS[1])

    def _assert_responses(self, question: str) -> None:
        assert_test(
            self.make_test_case(question, prompt_openai(self.MAINTAIN_PROMPT, question)),
            self.METRICS,
            run_async=False,
        )


if __name__ == '__main__':
    main()
