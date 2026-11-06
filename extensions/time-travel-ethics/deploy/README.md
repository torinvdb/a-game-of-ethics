# Container and Kubernetes path for the Ink cluster scenario

**Status (6 Nov 2026 review).** The image and Job now run the **Ink cluster scenario**
(`tools/demo.py`: inkjs compile, seven scripted replays, one rejected adapter, paired
label probes) instead of the earlier generic Python calibration, then write an evidence
manifest and POST OTLP spans to the collector.

| Path | Status |
| --- | --- |
| `docker build -f deploy/Dockerfile -t ethics-lab:0.2.0 .` (from the extension root) | **Executed**: Docker 29.9.2, node:22-slim + python:3.12-slim |
| Container run, read-only root, UID 10001, all caps dropped, 256 MiB / 1 CPU, internal Docker network with `otel/opentelemetry-collector:0.123.0` | **Executed** (re-run 6 Nov on the current tree): exit 0; collector logged `"spans": 1062`; 77/77 Job outputs match `docs/agentic-ethics/evidence/manifest.json`. The 8 `*.deepeval.json` files that manifest lists are not produced, because the image has no DeepEval and the Job does not pass `--deepeval-python`, so a whole-manifest verify reports them missing |
| Overwrite of an existing `RUN_ID` | **Executed**: refused (exit 1) |
| Collector unreachable | **Executed**: job fails (exit 1), does not silently pass |
| Egress probe to a public host from the job | **Executed at Docker level only** (internal network): blocked. Not a NetworkPolicy test |
| `kubectl kustomize deploy` + `kubeconform -strict` (Kubernetes 1.32 schemas) | **Executed**: 7/7 resources valid; Flux example 2/2 valid against CRD schemas |
| kind v0.27.0 cluster | **Attempted twice, failed**: nested runc cannot start CRI pod sandboxes (`can't get final child's PID from pipe`), also with `snapshotter = "native"`; plain `ctr run` inside the node works |
| Real kube-apiserver v1.32.13 + etcd 3.5.21 + kube-controller-manager (no kubelet), RBAC + PodSecurity admission | **Executed** (checksum-verified binaries): server-side apply of `kubectl kustomize deploy`; Job pod admitted under `restricted:v1.32`; privileged variant **rejected** by PSA; `auth can-i --list` for `ethics-evaluator` = self-review rules only; NetworkPolicy accepted and selectors match the pods; PVC binds to a static PV; Job fails `DeadlineExceeded` with no node; namespace deletion removes every namespaced object |
| Pod execution, NetworkPolicy *enforcement* (needs a CNI), PVC writes, Service routing to ready pods, Flux reconciliation | **Not executed** |
| Signed manifest (`tools/sign-evidence.py`, ed25519) checked by `verify-evidence.py --signature --allowed-signers` | **Executed** on rehearsal evidence with a throwaway key; tampered manifest exits 2 |

Commands, outputs and the three manifest fixes the apiserver run prompted (PSA version
pin, dedicated ServiceAccounts, DNS egress limited to `k8s-app: kube-dns`) are in
`docs/agentic-ethics/evidence/deploy-v2-notes.md`.

## Build

```sh
cd extensions/time-travel-ethics
docker build -f deploy/Dockerfile -t ethics-lab:0.2.0 .
# Behind a TLS-intercepting proxy, supply its CA as an optional build secret:
#   docker build --secret id=ca,src=/path/ca.pem -f deploy/Dockerfile -t ethics-lab:0.2.0 .
```

The runtime stage has no package-manager step. inkjs is pinned exactly in
`deploy/runtime/package-lock.json` (with integrity hash). Pin both base images by
digest before publishing; the tags here are examples.

## Container-level rehearsal (no cluster)

```sh
docker network create --internal ethics-lab-net
docker run -d --name otel-collector --network ethics-lab-net --read-only --user 10001 \
  -v "$PWD/otel:/etc/otel:ro" otel/opentelemetry-collector:0.123.0 --config=/etc/otel/config.yaml
# otel/config.yaml = the config.yaml block from deploy/collector.yaml
mkdir -p evidence && sudo chown 10001:10001 evidence
docker run --rm --network ethics-lab-net --read-only --memory 256m --cpus 1 --user 10001:10001 \
  --cap-drop ALL --security-opt no-new-privileges -e RUN_ID=rehearsal-001 \
  -v "$PWD/evidence:/evidence" ethics-lab:0.2.0
docker logs otel-collector | grep Traces
python3 tools/verify-evidence.py evidence/rehearsal-001 ../../docs/agentic-ethics/evidence/manifest.json --optional "*.deepeval.json"
docker rm -f otel-collector && docker network rm ethics-lab-net
```

## Signing evidence

```sh
python3 tools/sign-evidence.py keygen --out-dir ~/secure/ethics-keys   # refuses a git work tree
python3 tools/sign-evidence.py sign evidence/rehearsal-001/evidence-manifest.json \
  --key ~/secure/ethics-keys/evidence-signing.key
python3 tools/verify-evidence.py evidence/rehearsal-001 evidence/rehearsal-001/evidence-manifest.json \
  --signature evidence/rehearsal-001/evidence-manifest.json.sig.json --allowed-signers ALLOWED_SIGNERS
```

The trust anchor is the public key published out of band (release notes or a signed git
tag), not a copy stored next to the evidence. Never commit the private key.

## Disposable cluster (pod execution not yet executed)

1. Select a disposable cluster/context explicitly. Never run the co-speaker starter's
   destructive reset against an existing cluster.
2. Load the image (`kind load docker-image ethics-lab:0.2.0`) or push it to your own
   registry and replace the image field.
3. Verify a default StorageClass and a CNI that enforces NetworkPolicy. Apply
   `namespace.yaml`, `serviceaccounts.yaml`, `evidence.yaml`, `collector.yaml`, `network.yaml`; wait for
   `deployment/otel-collector`; then apply `job.yaml` (`kubectl apply -k deploy` applies all,
   but the Job may start before the collector is ready and will then fail by design).
4. Expected evidence: `kubectl -n ethics-lab logs job/ethics-ink-001` ends with
   `collector accepted 1062 spans: HTTP 200` and `egress probe blocked as expected`; the
   collector log shows `"spans": 1062`. If the egress probe succeeds the Job exits 3:
   the CNI is not enforcing the policy.
5. Evidence persists on PVC `evidence` under `/evidence/<RUN_ID>` with
   `evidence-manifest.json`. Copy it out with an authorized reader pod before deleting the
   namespace/PVC: with a `reclaimPolicy: Delete` StorageClass, namespace deletion destroys it. Re-running needs a new Job name and `RUN_ID`.
6. Flux: `flux-example.yaml` needs a published repository URL and immutable commit. Flux
   reconciles configuration; it does not advance the simulated clock.

Admission, RBAC, selectors and namespace cleanup were checked against a real apiserver
(see the notes file). Still open: a kind/k3d run on a host that supports nested
containers, recording `kubectl get events`, the Job log, the collector log and the PVC
contents after pod deletion.

The collector logs metadata, not decision content. OTLP spans carry action hashes,
logical months and outcome classes; timestamps are export time, not execution latency.
No agent service-account token is mounted and the evaluated policy never receives
Kubernetes API access. Live external model use would need an explicit egress design.
