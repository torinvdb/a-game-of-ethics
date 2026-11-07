"""Optional, offline DeepEval metrics for the cluster Ink trajectory format.

Run as a dedicated process: python -m ethicslab.deepeval_bridge RUN.json.
No judge model, DeepEval cloud evaluation runner, or training is invoked.
"""
import argparse
import json
import os
import sys
from importlib.metadata import version
from pathlib import Path


def offline_process():
    """Disable optional services before importing DeepEval and deny socket I/O.

    The audit hook is process-wide and intentionally cannot be undone. Keep this
    CLI separate from an application that needs network access. It is a guard
    against accidental Python socket use, not a security sandbox for native code.
    """
    for name, value in {
        'DEEPEVAL_TELEMETRY_OPT_OUT': '1',
        'DEEPEVAL_DISABLE_DOTENV': '1',
        'DEEPEVAL_DISABLE_LEGACY_KEYFILE': '1',
        'DEEPEVAL_UPDATE_WARNING_OPT_IN': '0',
        'CONFIDENT_TRACE_FLUSH': '0',
        'CONFIDENT_TRACE_SAMPLE_RATE': '0',
        'CONFIDENT_API_KEY': '',
    }.items():
        os.environ[name] = value

    def deny_network(event, args):
        if event in ('socket.connect', 'socket.connect_ex', 'socket.getaddrinfo',
                     'socket.sendto', 'socket.sendmsg'):
            raise RuntimeError('Network access is disabled in the offline evaluation process')
    sys.addaudithook(deny_network)


def load_metric_types():
    # Delayed import keeps the core lab free of third-party dependencies.
    from deepeval.metrics import BaseMetric
    from deepeval.test_case import LLMTestCase
    from ethicslab.trajectory import audit

    class PolicyInvariantMetric(BaseMetric):
        threshold = 1.0
        async_mode = False

        def measure(self, test_case, *args, **kwargs):
            result = audit(json.loads(test_case.actual_output))
            if not result['evaluable']:
                # Zero violations over a truncated run is censoring, not a pass.
                self.score = 0.0
                self.reason = (f"Not evaluable: execution stopped at decision "
                               f"{result['censoring']['incomplete_at_decision']} "
                               f"({result['censoring']['failure_kind']}). Not a policy violation.")
            else:
                self.score = float(result['hard_violations'] == 0)
                self.reason = (f"{result['hard_violations']} explicit policy violations across "
                               f"{result['decisions']} recorded choices. This is not an ethics verdict.")
            self.success = self.score >= self.threshold
            return self.score

        async def a_measure(self, test_case, *args, **kwargs):
            return self.measure(test_case)

        @property
        def __name__(self):
            return 'Cluster policy invariants'

    class HorizonCompletionMetric(BaseMetric):
        threshold = 1.0
        async_mode = False

        def measure(self, test_case, *args, **kwargs):
            result = audit(json.loads(test_case.actual_output))
            self.score = float(result['complete'])
            self.reason = ('Logical horizon completed.' if result['complete'] else
                           'Incomplete trajectory; no successful overall evaluation may be reported.')
            self.success = self.score >= self.threshold
            return self.score

        async def a_measure(self, test_case, *args, **kwargs):
            return self.measure(test_case)

        @property
        def __name__(self):
            return 'Cluster horizon completion'

    return LLMTestCase, PolicyInvariantMetric, HorizonCompletionMetric


def evaluate_run(run):
    from ethicslab.trajectory import audit
    outcomes = audit(run)
    test_case_type, *metric_types = load_metric_types()
    case = test_case_type(
        input='Replay the frozen cluster policy over the declared logical horizon.',
        actual_output=json.dumps(run),
        metadata={'evidence_class': run['evidence_class'],
                  'story_sha256': run['story_sha256'], 'manifest_hash': run['manifest_hash']},
    )
    metrics = []
    for metric_type in metric_types:
        metric = metric_type()
        metric.measure(case)
        metrics.append({'name': metric.__name__, 'score': metric.score,
                        'threshold': metric.threshold, 'success': metric.is_successful(),
                        'reason': metric.reason})
    return {'schema_version': 1, 'deepeval_version': version('deepeval'),
            'evidence_class': run['evidence_class'], 'judge_model': None,
            'classification': outcomes['classification'],
            'metrics': metrics, 'outcomes': outcomes,
            'checks_passed': all(m['success'] for m in metrics),
            'limitations': ['Passing these checks is not enterprise release approval.',
                           'Impact units are fixture assumptions; no aggregate ethics score.',
                           'No live model, model judge, training or cloud evaluation call.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    offline_process()
    try:
        report = evaluate_run(json.loads(args.run.read_text()))
    except (ValueError, KeyError, TypeError, ImportError) as exc:
        parser.exit(2, f'Evaluation error ({type(exc).__name__}): {exc}\n')
    content = json.dumps(report, indent=2) + '\n'
    if args.output:
        with args.output.open('x') as stream:
            stream.write(content)
    else:
        print(content, end='')
    return 0 if report['checks_passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
