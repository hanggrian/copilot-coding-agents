from unittest import main

from deepeval import assert_test
from deepeval.metrics.g_eval.g_eval import SingleTurnParams

from .llms import OPENAI_REVIEWER_MODEL, prompt_openai
from .tests import StructureTestCase, QualityTestCase


class TestInspectStructure(StructureTestCase):
    INSPECT_FULL = StructureTestCase.load_full('agents/Inspect.agent.md')
    PLAN_FULL = StructureTestCase.load_full('agents/template/Plan.agent.md')

    def test_inspect(self) -> None:
        lowered = self.INSPECT_FULL.lower()
        self.assertIn('# inspect', lowered, 'Inspect: missing H1 role heading')
        self.assertIn(
            'stop if you consider running file editing tools',
            lowered,
            'Inspect: missing read-only editing guard',
        )
        self.assertIn('never', lowered, 'Inspect: missing explicit prohibition ("NEVER ...")')
        self.assertIn('workflow', lowered, 'Inspect: missing workflow section')
        self.assertIn('report', lowered, 'Inspect: missing report terminology')
        self.assertIn('style guide', lowered, 'Inspect: missing style guide section')
        self.assertIn('bug', lowered, 'Inspect: missing bug concept')
        self.assertIn('reproduce', lowered, 'Inspect: missing reproduction concept')
        self.assertIn('vulnerabilities', lowered, 'Inspect: missing vulnerabilities concept')
        self.assertIn('severity', lowered, 'Inspect: missing severity concept')
        self.assertIn('high', lowered, 'Inspect: missing severity level reference')
        self.assertIn('empathetic', lowered)
        self.assertIn('evidence-based', lowered)
        self.assertIn(
            'run terminal commands',
            lowered,
            'Inspect: missing terminal testing capability',
        )

    def test_plan(self) -> None:
        lowered = self.PLAN_FULL.lower()
        self.assertIn('you are', lowered, 'Plan: missing role definition ("You are ...")')
        self.assertIn(
            'stop if you consider running file editing tools',
            lowered,
            'Plan: missing read-only editing guard',
        )
        self.assertIn('never', lowered, 'Plan: missing explicit prohibition ("NEVER ...")')
        self.assertIn('workflow', lowered, 'Plan: missing workflow section')
        self.assertIn('plan_style_guide', lowered, 'Plan: missing style guide section')
        self.assertIn(
            'changes requested',
            lowered,
            'Plan: missing refinement loop pattern',
        )


class TestInspectQuality(QualityTestCase):
    INSPECT_PROMPT = QualityTestCase.load_prompt('agents/Inspect.agent.md')
    PLAN_PROMPT = QualityTestCase.load_prompt('agents/template/Plan.agent.md')

    INSPECT_METRICS = [
        QualityTestCase.prompt_quality_metric(
            'Bug Report Structure',
            'Does the response follow a bug report format with affected components, ' +
            'reproduction steps, expected vs actual behavior, and a patch suggestion?',
            [SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
            model=OPENAI_REVIEWER_MODEL,
        ),
        QualityTestCase.prompt_quality_metric(
            'Read-Only Enforcement',
            'Does the response report findings and suggest conceptual fixes without ' +
            'proposing to directly edit or modify source files? The agent may include ' +
            'illustrative code in a proof-of-concept or patch suggestion as part of the ' +
            'report, but must not instruct the user to apply edits, provide file paths ' +
            'to modify, or frame the response as an implementation guide.',
            [SingleTurnParams.ACTUAL_OUTPUT],
            model=OPENAI_REVIEWER_MODEL,
        ),
        QualityTestCase.prompt_quality_metric(
            'No Empathetic Language',
            "Does the response avoid complimentary or apologetic language (no 'Great " +
            "question!', 'Sorry about that', etc.)?",
            [SingleTurnParams.ACTUAL_OUTPUT],
            model=OPENAI_REVIEWER_MODEL,
        ),
        QualityTestCase.prompt_quality_metric(
            'Severity Level',
            'Does the bug report include a severity level (High, Medium, Low, or ' +
            'Unknown) for each vulnerability?',
            [SingleTurnParams.ACTUAL_OUTPUT],
            model=OPENAI_REVIEWER_MODEL,
        ),
    ]
    PLAN_METRICS = [
        QualityTestCase.prompt_quality_metric(
            'No Bug Report Format',
            'Does the response avoid following a bug report format? It should present a ' +
            'plan with steps and structure, not a vulnerability report with affected ' +
            'components and reproduction steps.',
            [SingleTurnParams.ACTUAL_OUTPUT],
            model=OPENAI_REVIEWER_MODEL,
        ),
        QualityTestCase.prompt_quality_metric(
            'No Terminal Command Execution',
            'Does the response avoid suggesting running terminal commands?',
            [SingleTurnParams.ACTUAL_OUTPUT],
            model=OPENAI_REVIEWER_MODEL,
        ),
    ]

    QUESTION = \
        'A double-submit race condition is a common web vulnerability where users ' + \
        'clicking a submit button twice creates duplicate records because the server ' + \
        'handler lacks an idempotency check. Produce a report on this vulnerability ' + \
        'class covering affected components, reproduction, impact, and mitigation.'
    PLAN_QUESTION = \
        'Create a plan to implement duplicate-submission protection for a web form. ' + \
        'The form currently allows double-clicks to create duplicate database records. ' + \
        'Include steps for idempotency tokens, database constraints, and client-side ' + \
        'prevention. Do not ask follow-up questions.'
    EXTRA_QUESTIONS = [
        'What causes connection pool exhaustion in backend services and how can it ' +
        'be prevented?',
        'Why does stale closure occur in React useEffect hooks and how can it be fixed?',
    ]

    def test_inspect_specific_rules(self) -> None:
        case = self.make_test_case(self.QUESTION, prompt_openai(self.INSPECT_PROMPT, self.QUESTION))
        for metric in self.INSPECT_METRICS:
            assert_test(case, [metric], run_async=False)

    def test_plan_lacks_inspect_features(self) -> None:
        case = \
            self.make_test_case(
                self.PLAN_QUESTION,
                prompt_openai(self.PLAN_PROMPT, self.PLAN_QUESTION),
            )
        for metric in self.PLAN_METRICS:
            assert_test(case, [metric], run_async=False)

    def test_question1(self) -> None:
        self._assert_responses(self.EXTRA_QUESTIONS[0])

    def test_question2(self) -> None:
        self._assert_responses(self.EXTRA_QUESTIONS[1])

    def _assert_responses(self, question: str) -> None:
        assert_test(
            self.make_test_case(question, prompt_openai(self.INSPECT_PROMPT, question)),
            self.METRICS,
            run_async=False,
        )


if __name__ == '__main__':
    main()
