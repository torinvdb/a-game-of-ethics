import copy
import unittest
from ethicslab.trajectory import audit, VIOLATIONS, OTHER_ACTIONS


def fixture(violation=False):
    action = sorted(VIOLATIONS if violation else OTHER_ACTIONS)[0]
    summary = dict(horizon=1, month=2, decision_count=1, hard_violations=int(violation),
                   medical_disruption=0, education_disruption=0, backlog=0,
                   delayed_batch_work=0, exposure_windows=0, overdue_exception_windows=0,
                   temporary_capacity_credits=6)
    before = dict(summary, month=1, decision_count=0, hard_violations=0)
    return dict(runtime='inkjs', complete=True, adapter_failure=None, summary=summary,
                records=[dict(index=0, state_before=before, selected=action,
                              choices=[{'text': action}])])


class TrajectoryTests(unittest.TestCase):
    def test_explicit_violation_recomputed(self):
        self.assertEqual(audit(fixture(True))['hard_violations'], 1)
        self.assertEqual(audit(fixture())['hard_violations'], 0)

    def test_forged_summary_rejected(self):
        run = fixture(True)
        run['summary']['hard_violations'] = 0
        with self.assertRaises(ValueError):
            audit(run)

    def test_unknown_or_unoffered_action_rejected(self):
        for action in ('A new unreviewed action', sorted(VIOLATIONS)[0]):
            run = fixture()
            run['records'][0]['selected'] = action
            with self.assertRaises(ValueError):
                audit(run)

    def test_truncated_run_is_incomplete_not_successful(self):
        run = fixture()
        run.update(complete=False, adapter_failure={'type': 'adapter_failure'}, records=[])
        run['summary'].update(decision_count=0, month=1)
        self.assertFalse(audit(run)['complete'])
        run['complete'] = True
        with self.assertRaises(ValueError):
            audit(run)

    def test_changed_counter_or_sequence_rejected(self):
        for key, value in [('decision_count', 4), ('hard_violations', 1), ('month', 5)]:
            run = fixture()
            run['records'][0]['state_before'][key] = value
            with self.assertRaises(ValueError):
                audit(run)

    def test_outcome_burdens_do_not_become_policy_violations(self):
        run = fixture()
        run['summary'].update(medical_disruption=84, education_disruption=0, backlog=36)
        result = audit(run)
        self.assertEqual(result['hard_violations'], 0)
        self.assertEqual(result['medical_disruption'], 84)
        self.assertEqual(result['backlog'], 36)
