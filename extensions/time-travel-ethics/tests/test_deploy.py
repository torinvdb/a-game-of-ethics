"""Offline consistency checks for the container/Job path and evidence verification.
These do not replace applying the manifests to a cluster."""
import hashlib, importlib.util, json, re, shutil, tempfile, unittest
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
