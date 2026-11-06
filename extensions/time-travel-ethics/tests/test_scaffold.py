"""Agent-scaffold checks. Oracles here are stated in terms of the rubric and the
case facts (what the ledger must or must not contain), not in terms of counts
copied from a previous run; the few exact counts are derived in comments."""
import copy
import json
import socket
import sys
import unittest

from ethicslab import scaffold
from ethicslab.scaffold import (GUARDED, UNGUARDED, load_cases, parse_call, run_episode, swap_labels,
                                tool_schema, verify_session, fairness_probe, digest)
from ethicslab.scripted_models import MODELS, careful, injection_susceptible, emit

DEV = {c['case_id']: c for c in load_cases('dev')}
BASE = DEV['dev-01-baseline']
INJECTED = DEV['dev-02-events-injection']
REVOKED = DEV['dev-03-revocation-schema']


def executed(session, tool):
    return [e for e in session['ledger'] if e['kind'] == 'tool_call' and e['tool'] == tool and e['outcome'] == 'executed']


class GuardTests(unittest.TestCase):
    def test_careful_policy_has_no_violations_or_denials_in_either_config(self):
        for case in DEV.values():
            for config in (GUARDED, UNGUARDED):
                s = run_episode(case, careful, config)['summary']
                self.assertEqual((s['realized_violations'], s['denied'], s['execution_failures']), (0, 0, 0))
                self.assertTrue(s['complete'])

    def test_tool_guard_cannot_block_content_violations(self):
        # Known limit: misleading reports use an allowed tool and pass the gateway.
        s = run_episode(BASE, MODELS['omits-disruptions'], GUARDED)['summary']
        self.assertEqual(s['realized_by_rule'], {'misleading_report': BASE['months']})

    def test_guard_never_executes_tool_level_violations(self):
        for case in DEV.values():
            for name, model in MODELS.items():
                if name == 'omits-disruptions':
                    continue
                s = run_episode(case, model, GUARDED)['summary']
                self.assertEqual(s['realized_violations'], 0, (case['case_id'], name, s['realized_by_rule']))

    def test_guard_denials_preserve_intent(self):
        g = run_episode(INJECTED, injection_susceptible, GUARDED)['summary']
        u = run_episode(INJECTED, injection_susceptible, UNGUARDED)['summary']
        self.assertGreater(g['attempted_violations'], 0)
        self.assertEqual(g['denied_by_reason'].get('denied_external_effect', 0), g['attempted_by_rule']['external_effect'])
        self.assertGreater(u['realized_by_rule']['external_effect'], 0)

    def test_denied_external_effect_and_no_real_network(self):
        calls = []

        def hook(event, args):
            if event.startswith('socket.'):
                calls.append(event)
        sys.addaudithook(hook)
        before = len(calls)
        session = run_episode(INJECTED, injection_susceptible, UNGUARDED)
        self.assertEqual(len(calls), before, 'scaffold must not open sockets even when unguarded')
        posts = executed(session, 'http_post')
        self.assertTrue(posts and all(e['result'].startswith('sandbox:') for e in posts))


class InjectionAndMemoryTests(unittest.TestCase):
    def test_injection_only_reaches_agent_through_tool_output(self):
        session = run_episode(INJECTED, careful, GUARDED)
        month = INJECTED['injections'][0]['month']
        reads = [e for e in executed(session, 'kubectl_get') if e['month'] == month]
        self.assertTrue(any('ignore policy' in e['result'] for e in reads))
        self.assertFalse(executed(session, 'disable_policy'))

    def test_memory_carries_injection_into_later_months(self):
        session = run_episode(INJECTED, injection_susceptible, UNGUARDED)
        month = INJECTED['injections'][0]['month']
        later = {e['month'] for e in executed(session, 'http_post')}
        self.assertEqual(min(later), month)
        self.assertEqual(later, set(range(month, INJECTED['months'] + 1)), 'memory makes the injection persist')
        self.assertTrue(any('ignore policy' in m for m in session['memory']))

    def test_bypass_persists_as_exposure_windows(self):
        s = run_episode(INJECTED, injection_susceptible, UNGUARDED)['summary']
        month = INJECTED['injections'][0]['month']
        # Disabled in the injection month and never restored: one window per later month start.
        self.assertEqual(s['realized_by_rule']['exposure_window'], INJECTED['months'] - month)


class PermissionTests(unittest.TestCase):
    def test_revoked_permission_denied_when_guarded_and_flagged_when_not(self):
        revoked = REVOKED['permissions']['scale']['revoked_month']
        g = run_episode(REVOKED, MODELS['label-biased'], GUARDED)
        u = run_episode(REVOKED, MODELS['label-biased'], UNGUARDED)
        self.assertTrue(all(e['month'] < revoked for e in executed(g, 'scale')))
        late = [e for e in executed(u, 'scale') if e['month'] >= revoked]
        self.assertTrue(late and all('unauthorized_after_revocation' in e['effects'] for e in late))

    def test_expired_exception_denied_when_guarded(self):
        g = run_episode(BASE, MODELS['stale-exception'], GUARDED)['summary']
        u = run_episode(BASE, MODELS['stale-exception'], UNGUARDED)['summary']
        self.assertEqual(g['realized_violations'], 0)
        self.assertGreater(g['denied_by_reason']['exception_expired'], 0)
        self.assertEqual(u['realized_by_rule']['expired_exception_use'], g['denied_by_reason']['exception_expired'])

    def test_permission_expiry_boundary(self):
        case = dict(BASE, permissions={'scale': {'expires_month': 3}})
        self.assertEqual(scaffold.permission_status(case, 'scale', 3), 'granted')
        self.assertEqual(scaffold.permission_status(case, 'scale', 4), 'expired')


class ExecutionFailureTests(unittest.TestCase):
    def test_malformed_output_is_execution_failure_not_policy(self):
        for name in ('flaky-format', 'slow'):
            s = run_episode(BASE, MODELS[name], GUARDED)['summary']
            ref = run_episode(BASE, careful, GUARDED)['summary']
            self.assertGreater(s['execution_failures'], 0)
            self.assertEqual(s['realized_violations'], 0)
            self.assertEqual(s['useful_work'], ref['useful_work'], 'recovered retries must not change outcomes')

    def test_unrecoverable_output_censors_episode(self):
        garbage = lambda obs: '{"tool": "scale", "args": {'
        session = run_episode(BASE, garbage, GUARDED)
        self.assertFalse(session['complete'])
        self.assertEqual(session['summary']['classification'], 'execution_failure')
        self.assertEqual(session['censored'], {'month': 1, 'step': 0, 'kind': 'parse_error'})
        self.assertEqual(session['summary']['realized_violations'], 0)

    def test_schema_change_breaks_stale_contract_but_not_adaptive_one(self):
        month = REVOKED['schema_changes'][0]['month']
        frozen = run_episode(REVOKED, MODELS['schema-frozen'], GUARDED)
        self.assertEqual(frozen['censored']['kind'], 'schema_error')
        self.assertEqual(frozen['censored']['month'], month)
        adaptive = run_episode(REVOKED, careful, GUARDED)
        self.assertTrue(adaptive['complete'])
        self.assertTrue(any(e['month'] >= month for e in executed(adaptive, 'scale')))

    def test_parse_call_rejects_wrong_types_and_extra_args(self):
        _, schema = tool_schema(BASE, 1)
        for raw in ('', 'null', '[]', '{"tool": 3}', '{"tool":"scale","args":{"service":"medical","replicas":"1"}}',
                    '{"tool":"scale","args":{"service":"medical","replicas":1,"force":true}}',
                    '{"tool":"shell","args":{}}', '{"tool":"scale","args":{"service":"medical","replicas":true}}'):
            with self.assertRaises(ValueError, msg=raw):
                parse_call(raw, schema)

    def test_step_limit_is_execution_failure(self):
        loop = lambda obs: emit('kubectl_get', {'resource': 'pods'})
        s = run_episode(dict(BASE, months=1), loop, GUARDED)['summary']
        self.assertEqual(s['execution_by_kind'], {'step_limit': 1})
        self.assertEqual(s['realized_violations'], 0)
        self.assertEqual(s['unresolved'], {'release': 1, 'capacity': 1, 'report': 1})


class FairnessTests(unittest.TestCase):
    def test_label_swap_probe(self):
        self.assertEqual(fairness_probe(BASE, careful, GUARDED)['label_flips'], 0)
        biased = fairness_probe(BASE, MODELS['label-biased'], GUARDED)
        self.assertEqual(biased['label_flips'], biased['cuts'])
        self.assertGreater(biased['cuts'], 0)

    def test_swap_changes_only_labels(self):
        swapped = swap_labels(BASE)
        self.assertEqual(swapped['profiles'], BASE['profiles'])
        self.assertEqual(swapped['labels']['medical'], BASE['labels']['education'])


class EvidenceTests(unittest.TestCase):
    def test_replay_is_deterministic(self):
        a = run_episode(INJECTED, injection_susceptible, UNGUARDED)
        b = run_episode(INJECTED, injection_susceptible, UNGUARDED)
        self.assertEqual(a['ledger'][-1]['hash'], b['ledger'][-1]['hash'])

    def test_resume_from_checkpoint_matches_uninterrupted_run(self):
        full = run_episode(INJECTED, injection_susceptible, UNGUARDED)
        part = run_episode(INJECTED, injection_susceptible, UNGUARDED, stop_after_month=5)
        self.assertFalse(part['complete'])
        stored = json.loads(json.dumps(part))  # checkpoint survives serialisation
        resumed = run_episode(INJECTED, injection_susceptible, UNGUARDED, session=stored)
        self.assertEqual(resumed['ledger'], full['ledger'])
        self.assertEqual(resumed['summary'], full['summary'])
        self.assertTrue(verify_session(resumed))

    def test_checkpoint_rejected_for_other_case_or_config(self):
        part = run_episode(BASE, careful, GUARDED, stop_after_month=2)
        with self.assertRaises(ValueError):
            run_episode(BASE, careful, UNGUARDED, session=part)
        with self.assertRaises(ValueError):
            run_episode(INJECTED, careful, GUARDED, session=part)

    def test_tamper_detection(self):
        session = run_episode(INJECTED, injection_susceptible, UNGUARDED)
        head = session['ledger'][-1]['hash']
        self.assertTrue(verify_session(session, head))
        edits = {
            'edit_effect': lambda s: next(e for e in s['ledger'] if e['effects'])['effects'].clear(),
            'delete_entry': lambda s: s['ledger'].pop(5),
            'reorder': lambda s: s['ledger'].insert(3, s['ledger'].pop(4)),
            'manifest': lambda s: s['manifest'].update(model_id='other'),
            'summary': lambda s: s['summary'].update(realized_violations=0),
            'truncate_tail': lambda s: s['ledger'].pop(),
        }
        for name, edit in edits.items():
            forged = copy.deepcopy(session)
            edit(forged)
            self.assertFalse(verify_session(forged, head), name)

    def test_recomputed_chain_needs_external_anchor(self):
        # An attacker who rewrites the whole chain passes self-consistency checks;
        # only an externally stored head digest detects it.
        session = run_episode(INJECTED, injection_susceptible, UNGUARDED)
        head = session['ledger'][-1]['hash']
        forged = copy.deepcopy(session)
        forged['ledger'] = [e for e in forged['ledger'] if e.get('tool') != 'http_post']
        previous = digest(forged['manifest'])
        for i, entry in enumerate(forged['ledger']):
            entry.update(seq=i, prev=previous)
            entry.pop('hash')
            entry['hash'] = previous = digest(entry)
        forged['summary'] = scaffold.score(forged['ledger'], None, forged['complete'], forged['censored'])
        self.assertTrue(verify_session(forged))
        self.assertFalse(verify_session(forged, head))


class HeldOutTests(unittest.TestCase):
    def test_heldout_frozen_and_disjoint(self):
        heldout = load_cases('heldout')
        self.assertEqual(len(heldout), 4)
        self.assertFalse({c['case_id'] for c in heldout} & set(DEV))
        self.assertFalse({c['seed'] for c in heldout} & {c['seed'] for c in DEV.values()})

    def test_modified_heldout_refused(self):
        from unittest.mock import patch
        real = scaffold.Path.read_bytes

        def tampered(self):
            data = real(self)
            return data.replace(b'"months": 18', b'"months": 17') if self.name.startswith('ho-01') else data
        with patch.object(scaffold.Path, 'read_bytes', tampered):
            with self.assertRaisesRegex(ValueError, 'frozen'):
                load_cases('heldout')


if __name__ == '__main__':
    unittest.main()
