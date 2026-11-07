"""Compare a run directory with a recorded evidence manifest (SHA-256 per file),
optionally after checking an ed25519 signature over the manifest.

python3 tools/verify-evidence.py RUN_DIR MANIFEST.json [--inputs-root REPO]
    [--signature MANIFEST.sig.json --allowed-signers ALLOWED_SIGNERS [--principal NAME]]

MANIFEST may be docs/agentic-ethics/evidence/manifest.json ("outputs" and
optional "inputs" maps) or a Job's evidence-manifest.json ("files" map).
Exit 0 only if every listed file exists and matches. Unlisted files are
reported but do not fail. A matching hash shows the bytes equal the recorded
bytes; on its own it does not authenticate the manifest.

With --signature, the manifest's exact bytes must carry a valid ed25519
signature (made by tools/sign-evidence.py) from a key listed in
ALLOWED_SIGNERS, else exit 2 before any file is compared. ALLOWED_SIGNERS uses
the OpenSSH allowed-signers line shape: "<principal> ssh-ed25519 <base64>".
The trust anchor is that public key, obtained out of band (release notes, a
signed git tag, a second channel); a key read from the run's own storage
anchors nothing. Signature checks need the Python "cryptography" package.
"""
import argparse
import fnmatch, base64, hashlib, json, struct, sys
from pathlib import Path

SIGNATURE_NAMESPACE = 'a-game-of-ethics/evidence-manifest/v1'
SIGNATURE_FORMAT = 'ethics-evidence-signature/v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def signed_message(manifest_bytes):
    """Bytes actually signed: namespace (domain separation) + NUL + SHA-256 of the manifest bytes."""
    return SIGNATURE_NAMESPACE.encode() + b'\0' + hashlib.sha256(manifest_bytes).digest()


def openssh_public_key(raw):
    """Encode a 32-byte ed25519 public key as an OpenSSH 'ssh-ed25519 AAAA...' string."""
    def field(b):
        return struct.pack('>I', len(b)) + b
    return 'ssh-ed25519 ' + base64.b64encode(field(b'ssh-ed25519') + field(raw)).decode()


def parse_openssh_public_key(text):
    kind, blob = text.split()[:2]
    if kind != 'ssh-ed25519':
        raise ValueError(f'unsupported key type {kind!r}')
    data = base64.b64decode(blob, validate=True)
    fields, i = [], 0
    while i < len(data):
        (n,) = struct.unpack('>I', data[i:i + 4])
        fields.append(data[i + 4:i + 4 + n])
        i += 4 + n
    if len(fields) != 2 or fields[0] != b'ssh-ed25519' or len(fields[1]) != 32:
        raise ValueError('malformed ssh-ed25519 key')
    return fields[1]


def parse_allowed_signers(text):
    """Return [(principal, raw_public_key)]. Lines: '<principal>[,<principal>] ssh-ed25519 <b64> [comment]'."""
    signers = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split()
        if len(parts) < 3:
            raise ValueError(f'malformed allowed-signers line: {line!r}')
        raw = parse_openssh_public_key(' '.join(parts[1:3]))
        for principal in parts[0].split(','):
            signers.append((principal, raw))
    return signers


def verify_signature(manifest_bytes, signature, allowed_signers_text, principal=None):
    """Return {'ok': bool, 'reason': str, 'principal': str|None}. Never raises on bad input."""
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except ImportError:
        return {'ok': False, 'reason': 'python package "cryptography" not installed', 'principal': None}
    try:
        if signature.get('format') != SIGNATURE_FORMAT or signature.get('namespace') != SIGNATURE_NAMESPACE:
            return {'ok': False, 'reason': 'unknown signature format or namespace', 'principal': None}
        if signature.get('manifest_sha256') != hashlib.sha256(manifest_bytes).hexdigest():
            return {'ok': False, 'reason': 'manifest bytes differ from the signed manifest', 'principal': None}
        claimed = parse_openssh_public_key(signature['public_key'])
        sig = base64.b64decode(signature['signature'], validate=True)
        signers = parse_allowed_signers(allowed_signers_text)
    except (KeyError, ValueError, TypeError, struct.error) as exc:
        return {'ok': False, 'reason': f'malformed signature or allowed-signers: {exc}', 'principal': None}
    names = [p for p, raw in signers if raw == claimed and (principal is None or p == principal)]
    if not names:
        return {'ok': False, 'reason': 'signing key is not in allowed signers' + (f' for {principal}' if principal else ''),
                'principal': None}
    try:
        Ed25519PublicKey.from_public_bytes(claimed).verify(sig, signed_message(manifest_bytes))
    except InvalidSignature:
        return {'ok': False, 'reason': 'signature does not verify', 'principal': None}
    return {'ok': True, 'reason': 'valid', 'principal': names[0]}


def verify(run_dir, manifest, inputs_root=None, optional=()):
    expected = manifest.get('outputs') or manifest.get('files') or {}
    report = {'matched': [], 'mismatched': [], 'missing': [], 'skipped_optional': [], 'unlisted': [], 'inputs_changed': []}
    for name, digest in sorted(expected.items()):
        path = run_dir / name
        if not path.is_file():
            # optional outputs (e.g. DeepEval reports) may be absent; if present they must match
            (report['skipped_optional'] if any(fnmatch.fnmatch(name, g) for g in optional) else report['missing']).append(name)
        elif sha(path) != digest:
            report['mismatched'].append(name)
        else:
            report['matched'].append(name)
    listed = set(expected) | {'evidence-manifest.json'}
    report['unlisted'] = sorted(str(p.relative_to(run_dir)) for p in run_dir.rglob('*')
                                if p.is_file() and str(p.relative_to(run_dir)) not in listed)
    if inputs_root is not None:
        for name, digest in sorted(manifest.get('inputs', {}).items()):
            path = inputs_root / name
            if not path.is_file() or sha(path) != digest:
                report['inputs_changed'].append(name)
    report['ok'] = bool(report['matched']) and not (report['mismatched'] or report['missing'])
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('run_dir', type=Path)
    p.add_argument('manifest', type=Path)
    p.add_argument('--inputs-root', type=Path)
    p.add_argument('--signature', type=Path, help='signature JSON from tools/sign-evidence.py')
    p.add_argument('--allowed-signers', type=Path, help='trusted public keys, obtained out of band')
    p.add_argument('--principal', help='require this signer identity from the allowed-signers file')
    p.add_argument('--optional', action='append', default=[], metavar='GLOB',
                   help='listed outputs matching GLOB may be absent (repeatable)')
    a = p.parse_args()
    if bool(a.signature) != bool(a.allowed_signers):
        p.error('--signature and --allowed-signers go together')
    manifest_bytes = a.manifest.read_bytes()
    if a.signature:
        sig = verify_signature(manifest_bytes, json.loads(a.signature.read_text()),
                               a.allowed_signers.read_text(), a.principal)
        print(json.dumps({'signature': sig}, indent=1))
        if not sig['ok']:
            return 2
    report = verify(a.run_dir, json.loads(manifest_bytes), a.inputs_root, a.optional)
    print(json.dumps({k: (v if k in ('ok',) or len(v) < 30 else f'{len(v)} files') for k, v in report.items()}, indent=1))
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
