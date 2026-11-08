"""Unit tests for the E1b cluster runner: budget-aware scheduling and path handling.

  python3 -m unittest discover -s benchmark/run -p 'test_*.py'
"""
import os
import sys
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cluster  # noqa: E402


class ScheduleTests(unittest.TestCase):
    def test_no_job_starts_once_budget_is_spent(self):
        started = []
        def work(job):
            started.append(job)
            return {'cost': 5.0}
        results, spent, skipped = cluster.schedule(list(range(10)), work, lambda job, run: run['cost'],
                                                   budget=12.0, workers=1)
        # 5 + 5 = 10 < 12 -> third job starts; 15 >= 12 -> nothing else starts.
        self.assertEqual(started, [0, 1, 2])
        self.assertEqual(spent, 15.0)
        self.assertEqual(skipped, list(range(3, 10)))
        self.assertEqual(len(results), 3)

    def test_overshoot_is_bounded_by_workers(self):
        lock, inflight, peak = threading.Lock(), [0], [0]
        def work(job):
            with lock:
                inflight[0] += 1
                peak[0] = max(peak[0], inflight[0])
            with lock:
                inflight[0] -= 1
            return {'cost': 1.0}
        results, spent, skipped = cluster.schedule(list(range(20)), work, lambda job, run: run['cost'],
                                                   budget=4.0, workers=3)
        self.assertLessEqual(peak[0], 3)
        # Jobs are only started while spent < budget, so at most budget + workers - 1 jobs run.
        self.assertGreaterEqual(spent, 4.0)
        self.assertLessEqual(spent, 4.0 + 3 - 1)
        self.assertEqual(len(results) + len(skipped), 20)

    def test_all_jobs_run_under_budget(self):
        results, spent, skipped = cluster.schedule(list(range(6)), lambda j: {'cost': 0.1},
                                                   lambda job, run: run['cost'], budget=10.0, workers=2)
        self.assertEqual(sorted(j for j, _, _ in results), list(range(6)))
        self.assertEqual(skipped, [])


class CommandTests(unittest.TestCase):
    def test_live_replay_gets_a_load_tolerant_decision_budget(self):
        cmd = cluster.replay_command('claude-sonnet-5-5', Path('/s.json'), Path('/o.json'), dry_run=False)
        self.assertEqual(cmd[cmd.index('--decision-timeout-ms') + 1], str(cluster.DECISION_TIMEOUT_MS))
        self.assertGreaterEqual(cluster.DECISION_TIMEOUT_MS, 300000)

    def test_live_retries_fit_the_cluster_decision_budget(self):
        # Worst case per decision: every attempt times out, or every attempt is a 429 and the SDK
        # waits out a retry-after of up to 60 s. Either must fit inside the replay's budget.
        sys.path.insert(0, str(cluster.EXT))
        from ethicslab import anthropic_provider as ap
        r = cluster.CLUSTER_MAX_RETRIES
        worst = max(ap.REQUEST_TIMEOUT_S * (r + 1) + r * ap.BACKOFF_ALLOWANCE_S, (r + 1) * 5 + r * 60)
        self.assertLess(worst, cluster.DECISION_TIMEOUT_MS / 1000)
        self.assertGreaterEqual(r, 3)
        self.assertEqual(cluster.replay_env({})['ETHICS_ANTHROPIC_MAX_RETRIES'], str(r))

    def test_replay_source_reads_the_flag(self):
        src = (cluster.EXT / 'tools/replay-cluster.mjs').read_text()
        self.assertIn("arg('--decision-timeout-ms'", src)


class OpenAITests(unittest.TestCase):
    CFG = {'endpoint': 'https://openrouter.ai/api/v1/chat/completions', 'temperature': 1.0,
           'max_tokens': 16000, 'response_format': 'json_schema, action enum'}

    def test_env_routes_to_the_endpoint_with_the_config_settings(self):
        env = cluster.replay_env({'ETHICS_PROVIDER': 'anthropic', 'OPENROUTER_API_KEY': 'k'}, self.CFG)
        self.assertNotIn('ETHICS_PROVIDER', env)
        self.assertEqual((env['ETHICS_API_KEY'], env['ETHICS_TEMPERATURE'], env['ETHICS_MAX_TOKENS'], env['ETHICS_JSON_SCHEMA']),
                         ('k', '1.0', '16000', '1'))

    def test_command_passes_the_endpoint_for_live_runs_only(self):
        live = cluster.replay_command('m', Path('/s'), Path('/o'), False, self.CFG['endpoint'])
        self.assertEqual(live[live.index('--endpoint') + 1], self.CFG['endpoint'])
        self.assertNotIn('--endpoint', cluster.replay_command('m', Path('/s'), Path('/o'), True, self.CFG['endpoint']))

    def test_retries_fit_the_decision_budget(self):
        self.assertLess(cluster.OPENAI_TIMEOUT_S * 3 + 30 * 2, cluster.DECISION_TIMEOUT_MS / 1000)

    def test_bridge_extra_constrains_action_to_the_choices(self):
        sys.path.insert(0, str(cluster.EXT))
        from ethicslab.__main__ import openai_extra
        extra = openai_extra(['keep', 'delete'], {'ETHICS_TEMPERATURE': '1.0', 'ETHICS_MAX_TOKENS': '16000', 'ETHICS_JSON_SCHEMA': '1'})
        self.assertEqual((extra['temperature'], extra['max_tokens']), (1.0, 16000))
        self.assertEqual(extra['response_format']['json_schema']['schema']['properties']['action']['enum'], ['keep', 'delete'])
        self.assertEqual(openai_extra(['a'], {}), {})


class StageTests(unittest.TestCase):
    E1B = {'stages': {'full': {'reps': 3, 'budget_usd': 45}}}

    def test_config_values_by_default(self):
        self.assertEqual(cluster.stage_params(self.E1B, 'full', None, None), (3, 45))

    def test_cli_overrides(self):
        self.assertEqual(cluster.stage_params(self.E1B, 'full', 5, 40.0), (5, 40.0))


class PathTests(unittest.TestCase):
    def test_relative_paths_become_absolute(self):
        rel = Path('some/relative/dir')
        self.assertEqual(cluster.absolute(rel), Path(os.getcwd()) / rel)
        self.assertTrue(cluster.absolute(rel).is_absolute())


if __name__ == '__main__':
    unittest.main()
