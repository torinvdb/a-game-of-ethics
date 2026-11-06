"""Offline consistency checks for the container/Job path and evidence verification.
These do not replace applying the manifests to a cluster (see
docs/agentic-ethics/evidence/deploy-v2-notes.md for the apiserver run)."""
import hashlib, importlib.util, json, os, re, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPLOY = ROOT / 'deploy'


def load_tool(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), ROOT / 'tools' / name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DeployConsistencyTests(unittest.TestCase):
    def test_job_runs_ink_path_not_generic_calibration(self):
        job = (DEPLOY / 'job.yaml').read_text()
        self.assertIn('deploy/run-ink-job.sh', job)
        self.assertNotIn('-m ethicslab', job)
        script = (DEPLOY / 'run-ink-job.sh').read_text()
        self.assertIn('tools/demo.py', script)
        self.assertIn('--post', script)

    def test_dockerfile_ships_everything_the_job_uses(self):
        docker = (DEPLOY / 'Dockerfile').read_text()
        for path in ('ethicslab', 'tools', 'scenarios', 'examples', 'cases', 'deploy/run-ink-job.sh',
                     'deploy/runtime/package-lock.json'):
            self.assertTrue(any(line.startswith('COPY') and path in line for line in docker.splitlines()), path)
            self.assertTrue((ROOT / path).exists(), path)
        self.assertIn('/usr/local/bin/node', docker)
        self.assertRegex(docker, r'USER 10001:10001')

    def test_image_tag_and_labels_agree(self):
        job, network = (DEPLOY / 'job.yaml').read_text(), (DEPLOY / 'network.yaml').read_text()
        collector = (DEPLOY / 'collector.yaml').read_text()
        tag = re.search(r'image: (ethics-lab:\S+)', job).group(1)
        self.assertIn(tag, (DEPLOY / 'README.md').read_text())
        self.assertIn('app: ethics-calibration', job)
        self.assertIn('matchLabels: {app: ethics-calibration}', network)
        self.assertIn('matchLabels: {app: otel-collector}', network)
        self.assertIn('labels: {app: otel-collector}', collector)
        self.assertIn('automountServiceAccountToken: false', job)

    def test_runtime_lock_pins_exact_inkjs(self):
        pkg = json.loads((DEPLOY / 'runtime/package.json').read_text())
        lock = json.loads((DEPLOY / 'runtime/package-lock.json').read_text())
        self.assertRegex(pkg['dependencies']['inkjs'], r'^\d+\.\d+\.\d+$')
        self.assertEqual(lock['packages']['node_modules/inkjs']['version'], pkg['dependencies']['inkjs'])
        self.assertTrue(lock['packages']['node_modules/inkjs']['integrity'].startswith('sha512-'))


class ManifestHardeningTests(unittest.TestCase):
    """Regression pins for problems found when the manifests met a real kube-apiserver."""

    def test_kustomization_lists_every_manifest(self):
        listed = re.findall(r'^  - (\S+)$', (DEPLOY / 'kustomization.yaml').read_text(), re.M)
        on_disk = {p.name for p in DEPLOY.glob('*.yaml')} - {'kustomization.yaml', 'flux-example.yaml'}
        self.assertEqual(set(listed), on_disk)

    def test_psa_restricted_is_version_pinned_with_warn_and_audit(self):
        ns = (DEPLOY / 'namespace.yaml').read_text()
        for mode in ('enforce', 'warn', 'audit'):
            self.assertIn(f'pod-security.kubernetes.io/{mode}: restricted', ns)
            self.assertRegex(ns, rf'pod-security.kubernetes.io/{mode}-version: v1\.\d+')
        self.assertNotIn('-version: latest', ns)

    def test_pod_templates_meet_restricted_profile(self):
        for name in ('job.yaml', 'collector.yaml'):
            text = (DEPLOY / name).read_text()
            for needle in ('runAsNonRoot: true', 'seccompProfile: {type: RuntimeDefault}',
                           'allowPrivilegeEscalation: false', 'capabilities: {drop: [ALL]}',
                           'readOnlyRootFilesystem: true', 'automountServiceAccountToken: false'):
                self.assertIn(needle, text, f'{name}: {needle}')
            for forbidden in ('privileged: true', 'hostNetwork', 'hostPID', 'hostIPC', 'hostPath', 'runAsUser: 0'):
                self.assertNotIn(forbidden, text, f'{name}: {forbidden}')

    def test_pods_use_dedicated_service_accounts_without_bindings(self):
        sas = (DEPLOY / 'serviceaccounts.yaml').read_text()
        self.assertEqual(re.findall(r'metadata: \{name: (\S+)\}', sas), ['ethics-evaluator', 'otel-collector'])
        self.assertEqual(sas.count('automountServiceAccountToken: false'), 2)
        self.assertIn('serviceAccountName: ethics-evaluator', (DEPLOY / 'job.yaml').read_text())
        self.assertIn('serviceAccountName: otel-collector', (DEPLOY / 'collector.yaml').read_text())
        everything = ''.join(p.read_text() for p in DEPLOY.glob('*.yaml'))
        for kind in ('Role', 'ClusterRole', 'RoleBinding', 'ClusterRoleBinding'):
            self.assertNotRegex(everything, rf'kind: {kind}\b', 'least privilege: no RBAC grants')

    def test_dns_egress_targets_cluster_dns_pods_only(self):
        network = (DEPLOY / 'network.yaml').read_text()
        self.assertIn('namespaceSelector: {matchLabels: {kubernetes.io/metadata.name: kube-system}}, '
                      'podSelector: {matchLabels: {k8s-app: kube-dns}}', network)

    def test_no_private_key_material_in_extension(self):
        for path in ROOT.rglob('*'):
            if path.is_file() and path.suffix in ('.key', '.pem', '') and path.stat().st_size < 20000 \
                    and 'node_modules' not in path.parts and '.git' not in path.parts:
                try:
                    text = path.read_text()
                except UnicodeDecodeError:
                    continue
                self.assertNotIn('PRIVATE KEY-----', text, str(path))


class EvidenceVerificationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='evidence-'))
        self.addCleanup(shutil.rmtree, self.tmp)
        (self.tmp / 'replays').mkdir()
        (self.tmp / 'replays/a.json').write_text('{"a": 1}')
        (self.tmp / 'comparison.json').write_text('{}')
        self.manifest = {'outputs': {n: hashlib.sha256((self.tmp / n).read_bytes()).hexdigest()
                                     for n in ('replays/a.json', 'comparison.json')}}
        self.verify = load_tool('verify-evidence.py').verify

    def test_clean_run_matches(self):
        self.assertTrue(self.verify(self.tmp, self.manifest)['ok'])

    def test_tampered_missing_and_extra_files(self):
        (self.tmp / 'replays/a.json').write_text('{"a": 2}')
        (self.tmp / 'comparison.json').unlink()
        (self.tmp / 'injected.json').write_text('{}')
        r = self.verify(self.tmp, self.manifest)
        self.assertFalse(r['ok'])
        self.assertEqual((r['mismatched'], r['missing'], r['unlisted']),
                         (['replays/a.json'], ['comparison.json'], ['injected.json']))

    def test_tampered_manifest_detected(self):
        self.manifest['outputs']['comparison.json'] = '0' * 64
        self.assertEqual(self.verify(self.tmp, self.manifest)['mismatched'], ['comparison.json'])

    def test_empty_manifest_is_not_a_pass(self):
        self.assertFalse(self.verify(self.tmp, {'outputs': {}})['ok'])


try:
    import cryptography  # noqa: F401
    HAVE_CRYPTO = True
except ImportError:
    HAVE_CRYPTO = False


@unittest.skipUnless(HAVE_CRYPTO, 'python package "cryptography" not installed')
class EvidenceSignatureTests(unittest.TestCase):
    """Throwaway keys live in a temp dir outside the repo and are deleted after each test."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='evidence-sig-'))
        self.addCleanup(shutil.rmtree, self.tmp)
        self.signer = load_tool('sign-evidence.py')
        self.verifier = load_tool('verify-evidence.py')
        os.environ.pop('ETHICS_SIGNING_PASSPHRASE', None)
        self.key, _ = self.signer.keygen(self.tmp / 'keys', principal='release-2026-11')
        self.allowed = (self.tmp / 'keys/allowed_signers').read_text()
        (self.tmp / 'run').mkdir()
        (self.tmp / 'run/a.json').write_text('{"a": 1}')
        self.manifest = self.tmp / 'manifest.json'
        self.manifest.write_text(json.dumps({'outputs': {'a.json': hashlib.sha256(b'{"a": 1}').hexdigest()}}))
        self.sig = self.signer.sign(self.manifest, self.key)

    def check(self, manifest_bytes=None, sig=None, allowed=None, principal=None):
        return self.verifier.verify_signature(manifest_bytes if manifest_bytes is not None else self.manifest.read_bytes(),
                                              sig or self.sig, allowed or self.allowed, principal)

    def test_valid_signature(self):
        r = self.check(principal='release-2026-11')
        self.assertEqual((r['ok'], r['principal']), (True, 'release-2026-11'))
        self.assertEqual(oct((self.tmp / 'keys/evidence-signing.key').stat().st_mode & 0o777), '0o600')

    def test_tampered_manifest_rejected(self):
        tampered = self.manifest.read_bytes().replace(b'"a.json"', b'"b.json"')
        self.assertFalse(self.check(tampered)['ok'])
        forged = dict(self.sig, manifest_sha256=hashlib.sha256(tampered).hexdigest())
        r = self.check(tampered, forged)
        self.assertEqual((r['ok'], r['reason']), (False, 'signature does not verify'))

    def test_wrong_key_rejected(self):
        other_key, other_pub = self.signer.keygen(self.tmp / 'other')
        resigned = self.signer.sign(self.manifest, other_key)
        r = self.check(sig=resigned)
        self.assertEqual((r['ok'], r['reason']), (False, 'signing key is not in allowed signers'))
        # Swapping in the trusted public key without the trusted private key fails the math.
        r = self.check(sig=dict(resigned, public_key=self.sig['public_key']))
        self.assertEqual((r['ok'], r['reason']), (False, 'signature does not verify'))
        # A trusted key under the wrong principal is also refused.
        self.assertFalse(self.check(principal='someone-else')['ok'])

    def test_malformed_inputs_fail_closed(self):
        self.assertFalse(self.check(sig=dict(self.sig, signature='!!'))['ok'])
        self.assertFalse(self.check(allowed='release ssh-rsa AAAA')['ok'])
        self.assertFalse(self.check(sig={k: v for k, v in self.sig.items() if k != 'public_key'})['ok'])

    def test_keygen_refuses_git_worktree(self):
        with self.assertRaises(SystemExit):
            self.signer.keygen(ROOT / 'tmp-should-not-exist')
        self.assertFalse((ROOT / 'tmp-should-not-exist').exists())

    def test_cli_end_to_end(self):
        sig_path = self.tmp / 'manifest.json.sig.json'
        sig_path.write_text(json.dumps(self.sig))
        (self.tmp / 'allowed').write_text(self.allowed)
        base = [sys.executable, str(ROOT / 'tools/verify-evidence.py'), str(self.tmp / 'run'), str(self.manifest),
                '--signature', str(sig_path), '--allowed-signers', str(self.tmp / 'allowed')]
        self.assertEqual(subprocess.run(base, capture_output=True).returncode, 0)
        self.manifest.write_text(self.manifest.read_text() + ' ')
        self.assertEqual(subprocess.run(base, capture_output=True).returncode, 2)


class OptionalOutputs(unittest.TestCase):
    def test_optional_glob_skips_absent_but_checks_present(self):
        import importlib.util, tempfile, hashlib
        spec = importlib.util.spec_from_file_location('ve', Path(__file__).parents[1] / 'tools/verify-evidence.py')
        ve = importlib.util.module_from_spec(spec); spec.loader.exec_module(ve)
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / 'a.json').write_text('A')
            (d / 'x.deepeval.json').write_text('X')
            m = {'outputs': {'a.json': hashlib.sha256(b'A').hexdigest(),
                             'x.deepeval.json': hashlib.sha256(b'X').hexdigest(),
                             'y.deepeval.json': hashlib.sha256(b'Y').hexdigest()}}
            self.assertFalse(ve.verify(d, m)['ok'])
            r = ve.verify(d, m, optional=['*.deepeval.json'])
            self.assertTrue(r['ok']); self.assertEqual(r['skipped_optional'], ['y.deepeval.json'])
            (d / 'x.deepeval.json').write_text('tampered')
            self.assertFalse(ve.verify(d, m, optional=['*.deepeval.json'])['ok'])
