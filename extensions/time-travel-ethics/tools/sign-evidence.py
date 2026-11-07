"""Sign an evidence manifest with ed25519 (Python "cryptography" package).

python3 tools/sign-evidence.py keygen --out-dir DIR [--principal NAME]
python3 tools/sign-evidence.py sign MANIFEST.json --key DIR/evidence-signing.key [--out MANIFEST.json.sig.json]
python3 tools/verify-evidence.py RUN_DIR MANIFEST.json --signature MANIFEST.json.sig.json \
    --allowed-signers ALLOWED_SIGNERS

The signature covers the manifest's exact bytes (via SHA-256, with a namespace
for domain separation; see verify-evidence.signed_message). The manifest in
turn pins every output file by SHA-256, so one signature authenticates the run.

Key handling:
- The private key must never be committed or stored with the evidence.
  keygen refuses to write inside a git work tree; keep the key offline or in a
  secret store. Set ETHICS_SIGNING_PASSPHRASE to encrypt it at rest.
- The anchor is the PUBLIC key, published out of band: in the release notes,
  in a signed git tag message, or another channel the verifier already trusts.
  A public key copied from the same storage as the evidence anchors nothing,
  because whoever can rewrite the evidence can rewrite that key too.
- A signature shows who approved these bytes; it does not show that the run
  was honest or that the scenario measured what it claims.
"""
import argparse, base64, datetime, hashlib, importlib.util, json, os, sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location('verify_evidence', Path(__file__).with_name('verify-evidence.py'))
_verify = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_verify)


def _crypto():
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    except ImportError:
        sys.exit('sign-evidence: the Python "cryptography" package is required')
    return serialization, Ed25519PrivateKey


def _inside_git_worktree(path):
    for parent in [path, *path.parents]:
        if (parent / '.git').exists():
            return parent
    return None


def _passphrase():
    value = os.environ.get('ETHICS_SIGNING_PASSPHRASE')
    return value.encode() if value else None


def keygen(out_dir, principal='evidence-signer', allow_in_repo=False):
    serialization, Ed25519PrivateKey = _crypto()
    out_dir = Path(out_dir).resolve()
    repo = _inside_git_worktree(out_dir)
    if repo and not allow_in_repo:
        raise SystemExit(f'sign-evidence: refusing to write a private key inside git work tree {repo}')
    out_dir.mkdir(parents=True, exist_ok=True)
    key = Ed25519PrivateKey.generate()
    pw = _passphrase()
    enc = serialization.BestAvailableEncryption(pw) if pw else serialization.NoEncryption()
    private_path = out_dir / 'evidence-signing.key'
    fd = os.open(private_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as fh:
        fh.write(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, enc))
    raw = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    public = _verify.openssh_public_key(raw)
    (out_dir / 'evidence-signing.pub').write_text(public + '\n')
    (out_dir / 'allowed_signers').write_text(f'{principal} {public}\n')
    return private_path, public


def sign(manifest_path, key_path):
    serialization, _ = _crypto()
    manifest_bytes = Path(manifest_path).read_bytes()
    json.loads(manifest_bytes)  # refuse to sign something that is not a JSON manifest
    key = serialization.load_pem_private_key(Path(key_path).read_bytes(), password=_passphrase())
    raw = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return {
        'format': _verify.SIGNATURE_FORMAT,
        'namespace': _verify.SIGNATURE_NAMESPACE,
        'algorithm': 'ed25519',
        'manifest': Path(manifest_path).name,
        'manifest_sha256': hashlib.sha256(manifest_bytes).hexdigest(),
        'public_key': _verify.openssh_public_key(raw),
        'signed_at': datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(),
        'signature': base64.b64encode(key.sign(_verify.signed_message(manifest_bytes))).decode(),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    k = sub.add_parser('keygen', help='create a key pair and an allowed_signers file')
    k.add_argument('--out-dir', required=True, type=Path)
    k.add_argument('--principal', default='evidence-signer')
    k.add_argument('--allow-in-repo', action='store_true', help='tests only; never commit the key')
    s = sub.add_parser('sign', help='sign a manifest')
    s.add_argument('manifest', type=Path)
    s.add_argument('--key', required=True, type=Path)
    s.add_argument('--out', type=Path)
    a = p.parse_args()
    if a.cmd == 'keygen':
        private_path, public = keygen(a.out_dir, a.principal, a.allow_in_repo)
        print(f'private key (keep secret, never commit): {private_path}')
        print(f'public key (publish out of band): {public}')
        return 0
    out = a.out or a.manifest.with_name(a.manifest.name + '.sig.json')
    out.write_text(json.dumps(sign(a.manifest, a.key), indent=1) + '\n')
    print(f'signature: {out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
