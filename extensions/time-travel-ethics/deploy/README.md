# Optional cluster deployment — not cluster-tested

The supplied Job runs the earlier generic Python calibration, not the Ink cluster story. Running the Ink path in Kubernetes additionally needs Node/inkjs and a container entry point for that path; that deployment is not implemented here.

The local demo requires no cluster. These are reviewable deployment examples, not a claim of end-to-end Kubernetes/Flux/OTel validation.

1. Select a disposable cluster/context explicitly. Never run the supplied starter's destructive cluster reset against an existing cluster.
2. Build from the extension root: `docker build -f deploy/Dockerfile -t ethics-lab:0.1.0 .`. Load the image into your local cluster, or push to your own registry and replace the image field. For reproducible published deployments pin both images by digest; tag pins here are examples.
3. Verify a default StorageClass and network-policy-enforcing CNI. Apply `namespace.yaml`, `evidence.yaml`, `collector.yaml` and `network.yaml` in namespace `ethics-lab`; wait for `deployment/otel-collector` rollout before applying `job.yaml`. Alternatively manage a collector-first dependency through Flux.
4. Observe `kubectl -n ethics-lab logs job/ethics-calibration`; inspect job completion and collector logs. A collector export failure must fail the job, not silently pass.
5. Evidence persists on PVC `evidence`. Mount it in an authorized reader pod for export. Archive it before deleting the namespace/PVC. Re-running requires a new Job name and new output directory; the engine deliberately rejects overwrites.
6. Flux example needs a published repository URL and immutable commit; none was pushed. Do not apply placeholders. Flux reconciles code/configuration; it does not advance the simulated clock. A Job runs once. Use a versioned Job or CronJob after explicitly designing retention and lifecycle behavior.

The collector logs metadata, not decision content. OTLP files are retrospective decision-record exports, not instrumented latency measurements. Logical months are attributes; wall timestamps belong to export time. No claim of a live telemetry backend is made. Avoid putting prompts/PII in metric labels. The all-pod policy allows only collector traffic and cluster DNS; live external model use requires an explicit egress design. No agent service-account token is mounted.
