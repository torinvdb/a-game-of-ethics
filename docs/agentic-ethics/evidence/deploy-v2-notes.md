# Deploy v2 validation notes (6 Nov 2026)

Scope: `extensions/time-travel-ethics/deploy/`, `tools/verify-evidence.py`,
`tools/sign-evidence.py`, `tests/test_deploy.py`. Everything below was executed on this
host unless it is marked **not executed**. Commands are shortened: `kubectl` is the
downloaded v1.32.13 binary with a local kubeconfig; `$S` is a scratch directory outside
the repository.

## 1. Control plane without a kubelet

**What ran.** Real etcd, kube-apiserver and kube-controller-manager. There was no
kubelet, scheduler or CNI, so pods could be created and admitted but never ran.

**Binaries.** Each was checked against its published checksum with `sha256sum -c`, and
all four returned `OK`:

| Binary | Source | sha256 |
| --- | --- | --- |
| kube-apiserver v1.32.13 | dl.k8s.io (`.sha256`) | `02d8dfd9…cc9602` |
| kube-controller-manager v1.32.13 | dl.k8s.io (`.sha256`) | `475223ea…164cf7a` |
| kubectl v1.32.13 | dl.k8s.io (`.sha256`) | `db2ae479…703c4c` |
| etcd v3.5.21 (`etcd-v3.5.21-linux-amd64.tar.gz`) | GitHub release (`SHA256SUMS`) | `adddda4b…148501c` |

**Flags.**

- apiserver: `--authorization-mode=RBAC --enable-admission-plugins=PodSecurity --disable-admission-plugins=NodeRestriction`.
  It used client-certificate authentication and a service-account signing key. All
  certificates were throwaway and generated with openssl in `$S`.
- controller-manager: `--controllers='*' --use-service-account-credentials=true`.

### Apply

`kubectl apply --server-side -f <(kubectl kustomize deploy)`

- The original manifests applied: 7 objects, all `serverside-applied`.
- The fixed manifests applied: 9 objects, adding 2 ServiceAccounts.

### PodSecurity admission

**Allowed: the real Job.** The Job controller created `ethics-ink-001-*`
(`SuccessfulCreate`). The pod object was admitted with:

- `sa=ethics-evaluator`
- `automount=false`
- volumes: only `evidence`, so no projected token

**Rejected: a privileged variant.** This was the same Job with:

- `privileged: true`
- `allowPrivilegeEscalation: true`
- `runAsUser: 0`
- `hostNetwork: true`

Results:

- Submitted as a Job: the Job was accepted with a warning. The controller then logged
  `FailedCreate` three times:
  `pods "ethics-ink-priv-…" is forbidden: violates PodSecurity "restricted:latest": host namespaces (hostNetwork=true), privileged (…), allowPrivilegeEscalation != false (…), unrestricted capabilities (…), runAsNonRoot != true (…), runAsUser=0 (…), seccompProfile (…)`.
- Submitted as a bare Pod after the fix:
  `Error from server (Forbidden): … violates PodSecurity "restricted:v1.32"`.

**Existing pods.**
`kubectl label --dry-run=server --overwrite ns ethics-lab pod-security.kubernetes.io/enforce=restricted`
printed no warnings for the existing pods.

### RBAC

Command:
`kubectl auth can-i --list -n ethics-lab --as=system:serviceaccount:ethics-lab:ethics-evaluator`,
with the `--as-group` flags for `system:serviceaccounts`, `system:serviceaccounts:ethics-lab`
and `system:authenticated`.

The only resource rules returned were the built-in self-review defaults:

- `selfsubjectreviews` [create]
- `selfsubjectaccessreviews` [create]
- `selfsubjectrulesreviews` [create]

There were also discovery and health non-resource GETs.

Every one of these spot checks returned `no`:

- `get` and `list secrets`
- `list configmaps`
- `create pods/exec`
- `get` and `create pods`
- `patch jobs`
- `get pvc`
- cluster-scoped `create namespaces`, `create clusterrolebindings`, `delete nodes` and `create persistentvolumes`
- `list secrets -A`

No RoleBinding or ClusterRoleBinding names an `ethics-lab` subject.

### NetworkPolicy

`isolated-lab` was accepted. Its selectors match the pods:

| Selector | Matches |
| --- | --- |
| `podSelector: {}` | both pods |
| `app=ethics-calibration` | the Job pod |
| `app=otel-collector` | the collector pod |
| Service `otel-collector` (`{"app":"otel-collector"}`) | the collector pod |

The EndpointSlice existed but had no endpoints, because no pod was ever Ready. There
were no `k8s-app=kube-dns` pods, because there was no CoreDNS.

**Enforcement was not tested.** It needs a CNI that implements NetworkPolicy, such as
Calico or Cilium. An apiserver only stores the object.

### PVC

- With no StorageClass, the claim stayed `Pending` (`FailedBinding: no persistent volumes available … no storage class is set`).
- After a static 1Gi RWO hostPath PV was added, the PV controller bound the claim
  (`evidence Bound lab-evidence-pv`).
- Nothing was written to the volume, because no kubelet ran.

### Job without a node

After about 10 minutes the Job showed `Failed=True reason=DeadlineExceeded`.
`activeDeadlineSeconds: 600` makes it fail closed rather than hang.

### Namespace deletion

`kubectl delete ns ethics-lab --wait` took 11 s.

**Afterwards.** Each of these resource types listed 0 objects:

- pods, jobs, deployments and replicasets
- pvc, configmaps and serviceaccounts
- networkpolicies, services and endpointslices

The raw PodList was empty, and `etcdctl get --prefix --keys-only /registry` found no
key containing `ethics-lab`.

**The PV survived.** The Retain PV moved to `Released`. With a typical dynamic
StorageClass (`reclaimPolicy: Delete`), deleting the namespace destroys the evidence.
Copy the evidence out first.

### Fixes made after the apiserver run

Each fix is pinned by a test in `tests/test_deploy.py` (`ManifestHardeningTests`):

1. The PSA level showed as `restricted:latest`. `enforce-version`, `warn` and `audit` are
   now pinned to `v1.32`, so a cluster upgrade cannot change the profile silently.
2. Both pods ran as the shared `default` ServiceAccount, where any later RoleBinding on
   `default` would reach them. New `serviceaccounts.yaml` adds `ethics-evaluator` and
   `otel-collector`. Both have `automountServiceAccountToken: false` and no bindings.
3. DNS egress allowed the whole `kube-system` namespace on port 53. It is now limited
   to `k8s-app: kube-dns` pods in `kube-system`.

## 2. Real node retry: failed

Command: kind v0.27.0 with the cached `kindest/node@sha256:f2263459…` image. The kind
config used `containerdConfigPatches` with `snapshotter = "native"`.

**Error.** kubeadm `wait-control-plane` timed out. Every static pod sandbox failed with
the same error as last time:

`OCI runtime create failed: runc create failed: unable to start container process: can't get final child's PID from pipe: EOF`

**Things tried that did not help.**

- `enable_unprivileged_ports = false` and `enable_unprivileged_icmp = false`, followed by a containerd restart.

**Things that worked inside the node.**

- `ctr run` of `registry.k8s.io/pause:3.10`, with the native snapshotter and with `--runc-systemd-cgroup`.
- `unshare` of the pid, net, ipc, uts, mount, cgroup and user namespaces.

So plain nested runc works, but the CRI pod-sandbox spec does not. The root cause was
not found within the 15-minute limit. The host uses cgroup v1 and a Firecracker kernel
(6.18). The cluster was deleted afterwards.

## 3. Docker Job-style rehearsal (re-run on the current tree)

**Build.** The image was rebuilt with:

`docker build --network=host --secret id=ca,src=<proxy CA> --build-arg HTTPS_PROXY=… -f deploy/Dockerfile -t ethics-lab:0.2.0 .`

The build needs both the proxy CA and the proxy. Without them, `npm ci` fails with
`SELF_SIGNED_CERT_IN_CHAIN` or `ECONNREFUSED`.

**Run.** The container ran on an internal Docker network with
`otel/opentelemetry-collector:0.123.0`, using:

- `--read-only --user 10001:10001 --cap-drop ALL --security-opt no-new-privileges`
- 256m memory and 1 CPU

| Run | Result |
| --- | --- |
| `RUN_ID=rehearsal-v2-001` | Ended with `evidence manifest: 77 files`, `collector accepted 1062 spans: HTTP 200` and `egress probe blocked as expected`. Collector: `"spans": 1062` |
| `RUN_ID=rehearsal-v2-002` | Exit 0. File hashes identical to run 001 (77/77) |
| Overwrite of `rehearsal-v2-001` | Exit 1 (`FileExistsError`) |

**Verify against the docs manifest.**
`verify-evidence.py RUN docs/agentic-ethics/evidence/manifest.json --inputs-root <repo root>`
gave 77 matched, 0 mismatched, 0 inputs changed, and `ok: false`.

The failure comes from 8 missing `replays/*.deepeval.json` files. The current manifest
was generated with `--deepeval-python`, but the image has no DeepEval and the Job does
not pass that flag. This is a scope difference between the manifest and the Job, not a
change in output bytes. It was left unchanged: the manifest is not owned here.

`traces.otlp.json` is unlisted because it is written after `evidence-manifest.json`.

**Concurrent edit.** `scenarios/cluster-template.ink` and other inputs changed in the
working tree, but the docs manifest was regenerated against them. No output diverged.

## 4. Signed evidence

`tools/sign-evidence.py` uses ed25519 from the Python `cryptography` package
(50.0.1 here). `ssh-keygen` is not installed on this host, so `ssh-keygen -Y` could not
be used or tested for interoperability.

**What is signed.** The signature covers
`"a-game-of-ethics/evidence-manifest/v1" || NUL || SHA-256(manifest bytes)`. The
manifest already pins every output by SHA-256.

**Verifying.** `verify-evidence.py --signature SIG --allowed-signers FILE [--principal NAME]`
checks the signature first and exits 2 on any failure. The allowed-signers file uses the
OpenSSH line shape `principal ssh-ed25519 AAAA…`.

**Executed with a throwaway key in `$S`, never in the repo.**

| Case | Result |
| --- | --- |
| Signed the rehearsal's `evidence-manifest.json`, then verified | Exit 0 (`valid`, principal `throwaway-test`, 77/77 files) |
| One byte changed in the manifest | Exit 2 (`manifest bytes differ from the signed manifest`) |

**Tests** (`EvidenceSignatureTests`):

- valid signature
- tampered manifest, including a forged `manifest_sha256` field
- wrong key, including a swapped-in trusted public key
- wrong principal
- malformed inputs
- keygen refusing to write inside a git work tree
- the CLI end to end

**The anchor** is the public key, published out of band in the release notes or a
signed git tag message. A key read from the evidence storage anchors nothing. The
private key must never be committed: keygen refuses to write into a git work tree, and
a test checks that the extension holds no `PRIVATE KEY` material.

## Still impossible on this host

- Running pods: there is no working kubelet or CRI sandbox (section 2).
- Testing NetworkPolicy enforcement: there is no CNI.
- Writing to the PVC and Service routing to a ready pod.
- Flux reconciliation: there is no Flux controller and no published repository URL.
