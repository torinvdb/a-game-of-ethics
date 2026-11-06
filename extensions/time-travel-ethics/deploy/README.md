# Container and Kubernetes path for the Ink cluster scenario

**Status (6 Nov 2026 review).** The image and Job now run the **Ink cluster scenario**
(`tools/demo.py`: inkjs compile, seven scripted replays, one rejected adapter, paired
label probes) instead of the earlier generic Python calibration, then write an evidence
manifest and POST OTLP spans to the collector.

| Path | Status |
| --- | --- |
| `docker build -f deploy/Dockerfile -t ethics-lab:0.2.0 .` (from the extension root) | **Executed**: Docker 29.9.2, node:22-slim + python:3.12-slim |
| Container run, read-only root, UID 10001, all caps dropped, 256 MiB / 1 CPU, internal Docker network with `otel/opentelemetry-collector:0.123.0` | **Executed**: exit 0 in ~5 s; collector logged `"spans": 1062`; Ink outputs byte-identical to the recorded calibration hashes |
| Overwrite of an existing `RUN_ID` | **Executed**: refused (exit 1) |
| Collector unreachable | **Executed**: job fails (exit 1), does not silently pass |
| Egress probe to a public host from the job | **Executed at Docker level only** (internal network): blocked. Not a NetworkPolicy test |
| `kubectl kustomize deploy` + `kubeconform -strict` (Kubernetes 1.32 schemas) | **Executed**: 7/7 resources valid; Flux example 2/2 valid against CRD schemas |
| kind v0.27.0 cluster | **Attempted, failed**: nested runc in the sandbox could not start pod sandboxes (`can't get final child's PID from pipe`) |
| Kubernetes apply, NetworkPolicy enforcement, PSA `restricted` admission, RBAC, PVC persistence, collector Service routing, Flux reconciliation, cleanup | **Not executed** |

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
python3 tools/verify-evidence.py evidence/rehearsal-001 ../../docs/agentic-ethics/evidence/manifest.json
docker rm -f otel-collector && docker network rm ethics-lab-net
```

## Disposable cluster (not yet executed)

1. Select a disposable cluster/context explicitly. Never run the co-speaker starter's
   destructive reset against an existing cluster.
2. Load the image (`kind load docker-image ethics-lab:0.2.0`) or push it to your own
   registry and replace the image field.
3. Verify a default StorageClass and a CNI that enforces NetworkPolicy. Apply
   `namespace.yaml`, `evidence.yaml`, `collector.yaml`, `network.yaml`; wait for
   `deployment/otel-collector`; then apply `job.yaml` (`kubectl apply -k deploy` applies all,
   but the Job may start before the collector is ready and will then fail by design).
4. Expected evidence: `kubectl -n ethics-lab logs job/ethics-ink-001` ends with
   `collector accepted 1062 spans: HTTP 200` and `egress probe blocked as expected`; the
   collector log shows `"spans": 1062`. If the egress probe succeeds the Job exits 3:
   the CNI is not enforcing the policy.
5. Evidence persists on PVC `evidence` under `/evidence/<RUN_ID>` with
   `evidence-manifest.json`. Copy it out with an authorized reader pod before deleting the
   namespace/PVC. Re-running needs a new Job name and `RUN_ID`.
6. Flux: `flux-example.yaml` needs a published repository URL and immutable commit. Flux
   reconciles configuration; it does not advance the simulated clock.

What would close the remaining gaps: a kind/k3d run on a host that supports nested
containers, recording `kubectl get events`, the PSA admission result, the Job log,
collector log, a `kubectl auth can-i --list` for the Job's service account, the PVC
contents after pod deletion, and namespace deletion completing.

The collector logs metadata, not decision content. OTLP spans carry action hashes,
logical months and outcome classes; timestamps are export time, not execution latency.
No agent service-account token is mounted and the evaluated policy never receives
Kubernetes API access. Live external model use would need an explicit egress design.
