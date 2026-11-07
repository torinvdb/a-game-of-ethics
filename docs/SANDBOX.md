# Docker sandbox for agent evaluations

This page covers running the benchmark harness, and an agent under test, in containers that
cannot reach the network except where you allow it. It describes what the setup isolates,
what it does not, and the commands and outputs from the run that verified it (6 Nov 2026,
Docker 29.9.2, Compose v5.6.1, runc, overlayfs, Linux 6.18).

The agent protocol itself (`agoe.agent/v1`, `--agent-url`, `--agent-cmd`) is documented in
[AGENT-PROTOCOL.md](AGENT-PROTOCOL.md). This page assumes it.

## Files

| Path | Purpose |
| --- | --- |
| `Dockerfile` | Harness image `agoe-harness`: `benchmark/run/run.mjs` plus frozen scenarios. Offline (`--provider mock`) by default |
| `.dockerignore` | Allowlist build context: `src/`, `scenarios/`, `benchmark/` (no `runs/`), `examples/agents/`, `docker/harness/`, package files |
| `docker/harness/entrypoint.mjs` | Adds `--provider mock` (unless `--agent-url`/`--agent-cmd` is given) and `--out /out`; exports `/run/secrets/*` as env vars |
| `docker/agent-sandbox/Dockerfile` | Example image for the agent under test: `examples/agents/http_agent.py` on `python:3.13-slim-bookworm` |
| `docker/agent-sandbox/secrets_env.py` | Agent entrypoint: exports `/run/secrets/*` as env vars, then execs the agent |
| `docker/egress-proxy/` | `proxy.py`, a CONNECT-only allowlisting forward proxy (Python stdlib), and its Dockerfile |
| `docker-compose.yml` | `offline` and `live-agent` profiles |
| `Makefile` | `build`, `test-offline`, `sandbox-up`, `eval`, `sandbox-down`, `clean` |
| `docker/secrets/`, `docker/results/` | Git-ignored. Secret files and run outputs |

## Quick start

```sh
make build                      # three images
make test-offline               # mock eval, --network none -> docker/results/offline-mock/
make sandbox-up                 # agent container, offline profile
make eval                       # harness vs agent -> docker/results/offline-<timestamp>/
make sandbox-down
```

Live profile, where the agent may call its model API and nothing else:

```sh
make secrets                                    # creates docker/secrets/{agoe_agent_token,model_api_key}
printf '%s' "$MY_KEY" > docker/secrets/model_api_key
make sandbox-up PROFILE=live-agent EGRESS_ALLOWLIST=api.anthropic.com
make eval PROFILE=live-agent AGENT_NAME=my-agent
make sandbox-down
```

To test your own agent, replace the `COPY` and `CMD` lines in
`docker/agent-sandbox/Dockerfile` (or point the `image:` of the `agent`/`agent-live` services
at your image). It must serve `POST /start`, `/decide` and `/end` on port 8080. The harness
reaches it as `http://agent-under-test:8080` in both profiles.

The harness image can also be used on its own:

```sh
docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges \
  -v "$PWD/out:/out" agoe-harness:dev --stage smoke --budget-usd 1000
docker run --rm agoe-harness:dev --help
docker run --rm --entrypoint python3 agoe-harness:dev benchmark/manifest.py verify
```

`--budget-usd` is needed for mock runs because the mock provider reports notional token costs
and the smoke stage budget is $1. `analyze.py` and `stats.py` need numpy, which the image does
not include; run them on the host against the results directory.

## Topology

```
              sandbox network (internal: true, no IPv4 on the host bridge)
   +-----------+   HTTP + bearer token   +---------------+
   |  harness  | ----------------------> | agent / agent-|
   +-----------+                         |     live      |
        |                                +---------------+
   /out (bind mount)                            |  HTTPS_PROXY (live-agent only)
                                                v
                                         +--------------+   egress network   +-----------+
                                         | egress-proxy | -----------------> | allowlist |
                                         +--------------+   (normal bridge)  |  hosts    |
                                                                             +-----------+
```

- `sandbox` is `internal: true`: Docker adds no default route and no NAT, and the embedded
  DNS does not resolve external names.
- `internal: true` alone still leaves the host's bridge address (the network's gateway IP)
  reachable from containers, so any host service listening on `0.0.0.0` would be exposed to
  the agent. The network sets `com.docker.network.bridge.inhibit_ipv4: "true"`, so the host
  has no address on that bridge. This was measured both ways (see Verification).
- Only `egress-proxy` joins the `egress` network. The harness never has egress in either
  profile.

## Hardening applied

| Control | harness | agent | egress-proxy |
| --- | --- | --- | --- |
| User | `RESULTS_UID` (caller's UID, 10001 if caller is root) | 10001 | 10001 |
| Read-only root, `/tmp` tmpfs 16 MiB `noexec,nosuid,nodev` | yes | yes | yes |
| `cap_drop: [ALL]`, `no-new-privileges` | yes | yes | yes |
| `init: true` (tini as PID 1) | yes | yes | yes |
| pids / memory (no swap) / CPUs | 128 / 512 MiB / 2 | 64 / 256 MiB / 1 | 128 / 128 MiB / 0.5 |
| Writable paths | `/out` bind mount only | none | none |
| Shell, apt/dpkg, pip, setuid bits | shell kept (trusted code); pip removed | all removed | all removed |

Image notes:

- Base images are pinned by digest:
  `node:22-bookworm-slim@sha256:5ec23b7c…3e13d96d` (build stage only) and
  `python:3.13-slim-bookworm@sha256:a5a7017e…5c72` (runtime). The harness runtime is the
  Python image plus the `node` binary copied from the build stage; it has no package-manager
  step and builds offline after the first stage. `REGISTRY` (default `docker.io/library`)
  lets you pull the same digests through a mirror; a digest is content-addressed, so a mirror
  cannot substitute different content.
- `npm ci --omit=dev --ignore-scripts`. figlet's unused fonts (about 20 MB) and source maps are
  removed. The `node` binary (125 MB) dominates the size.
- OCI labels: `source`, `licenses` (MIT), `version`, `revision` (git commit via `make build`).
- Sizes on disk / compressed: harness 384 MB / 93 MB, agent sandbox 182 MB / 45 MB, proxy
  182 MB / 45 MB. The agent and proxy share the Python base layers.

## Secrets

- No secret is passed as a build argument, `ENV`, or `COPY`. Compose `secrets:` bind-mounts
  `docker/secrets/<file>` read-only at `/run/secrets/<name>`. Each entrypoint exports the file
  as an upper-cased environment variable inside its own process tree. The value does not show
  in `docker inspect` (checked: `Config.Env` lists only `PATH`, `LANG`, Python and `HOME`
  variables).
- `agoe_agent_token` is shared by the harness and the agent (`AGOE_AGENT_TOKEN`); the agent
  answers 401 without it.
- `model_api_key` is mounted only into `agent-live`, at `/run/secrets/anthropic_api_key` by
  default (so the agent sees `ANTHROPIC_API_KEY`). Set `MODEL_KEY_NAME=openai_api_key` (or
  similar) for an agent that reads a different variable.
- `docker/secrets/` is mode 0700 and the files 0644: Compose bind-mounts files unchanged, and
  the containers run as UID 10001, which must be able to read them. The directory mode keeps
  other host users out.
- Build-time CA for a TLS-intercepting proxy: `make build CA_BUNDLE=/path/ca.pem` passes it
  as `--secret id=ca,src=...`. It is mounted only for the `npm ci` step in the build stage and
  is not in any layer of the final image (checked below).

## Egress proxy

`docker/egress-proxy/proxy.py` accepts only `CONNECT host:port`. It does not terminate TLS, so
it sees host names and ports but not request bodies or API keys.

- `EGRESS_ALLOWLIST`: comma-separated `host`, `host:port` or `.suffix` (subdomains only).
  Port defaults to 443. Matching is exact and case-insensitive; `evil-api.anthropic.com` does
  not match `api.anthropic.com`. An empty list denies everything.
- After the allowlist check the proxy resolves the name once, refuses it unless an address is
  globally routable (so a DNS answer cannot point at `169.254.169.254`, RFC 1918 space or the
  host), and connects to that exact address. `EGRESS_ALLOW_PRIVATE=1` lifts this; use it only
  for tests.
- Plain `GET http://...` through the proxy is refused with 405.
- `EGRESS_UPSTREAM_PROXY=http://host:port` chains allowed tunnels through a parent proxy. In
  that mode the parent resolves names, so the private-address check does not apply.
- Each decision is one JSON line on stdout: `docker compose --profile live-agent logs egress-proxy`.

What the proxy does not do: it cannot tell what the agent sends to an allowlisted host. An
agent with a model API key can put anything into a prompt. If the model provider is in the
allowlist, the agent can send data out through it.

## Verification (6 Nov 2026)

Commands run in this repository. The base images were pulled through
`REGISTRY=mirror.gcr.io/library` because Docker Hub returned 429, and builds used
`BUILD_FLAGS=--network=host CA_BUNDLE=/root/.ccr/ca-bundle.crt` because this host's egress
goes through a TLS-intercepting proxy.

### Build and offline run

```
$ make build REGISTRY=mirror.gcr.io/library BUILD_FLAGS=--network=host CA_BUNDLE=/root/.ccr/ca-bundle.crt
#18 naming to docker.io/library/agoe-harness:dev done
#12 naming to docker.io/library/agoe-agent-sandbox:dev done
#10 naming to docker.io/library/agoe-egress-proxy:dev done

$ make test-offline
docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges \
  --pids-limit 128 --memory 512m --memory-swap 512m --cpus 1 \
  --tmpfs /tmp:size=16m,noexec,nosuid,nodev --user 10001:10001 \
  -v .../docker/results/offline-mock:/out agoe-harness:dev --stage smoke --budget-usd 1000
78/78 cells to run · provider mock · budget $1000 · spent $0.0000
{"completed":78,"errors":0,"spent_usd":1.688,"out":"/out"}
results: .../docker/results/offline-mock/results.jsonl (78 rows)
```

Inside the image: `id` gives `uid=10001`; `touch /app/x` and `touch /tmp/x` (without the
tmpfs) both fail with `Read-only file system`. `benchmark/manifest.py verify` gives
`PASS: manifest 2.0.2 (0 problem(s))`. `--agent-cmd "python3 -I examples/agents/stdio_agent.py"
--scenarios hostage-holdout` under `--network none` gave `{"completed":2,"errors":0,...}`.

### Compose, offline profile, end to end

```
$ make sandbox-up
 Container agoe-sandbox-agent-1 Healthy
$ make eval RUN=final-offline
26/26 cells to run · provider http · budget $1 · spent $0.0000
{"completed":26,"errors":0,"spent_usd":0,"out":"/out"}
results: .../docker/results/final-offline
```

`run.json` records `"agent": {"protocol": "agoe.agent/v1", "transport": "http",
"url": "http://agent-under-test:8080", "name": "reference-http-agent", "timeout_ms": 60000}`.

### Agent container cannot reach the network (offline profile)

Probe run with `docker compose --profile offline exec -T agent python3 -I -c ...`:

```
dns example.com -> FAIL gaierror [Errno -3] Temporary failure in name resolution
https example.com -> FAIL URLError <urlopen error [Errno -3] Temporary failure in name resolution>
tcp 1.1.1.1:443 -> FAIL OSError [Errno 101] Network is unreachable
tcp 8.8.8.8:53 -> FAIL OSError [Errno 101] Network is unreachable
metadata 169.254.169.254:80 -> FAIL OSError [Errno 101] Network is unreachable
```

`sh -c id` in the agent: `exec: "sh": executable file not found in $PATH`. From the harness
container, `fetch('https://example.com')` fails with `EAI_AGAIN`.

### Host reachability through the bridge

With a listener on the host at `0.0.0.0:18999`, and the network declared with only
`internal: true`:

```
network: [{"Subnet":"172.18.0.0/16","Gateway":"172.18.0.1"}] internal=true
172.18.0.1 REACHED b'hello-from-host'
HOST LISTENER got connection from ('172.18.0.2', 37408)
```

So `internal: true` alone does not isolate the agent from host services. With
`com.docker.network.bridge.inhibit_ipv4: "true"` (the shipped configuration):

```
network: [{"Subnet":"172.18.0.0/16"}] {"com.docker.network.bridge.inhibit_ipv4":"true"}
bridge ipv4: none [Errno 99] Cannot assign requested address
172.17.0.1 FAIL OSError [Errno 101] Network is unreachable
192.0.2.2 FAIL OSError [Errno 101] Network is unreachable
listener log: []
```

(`172.18.0.1` is then assigned to the first container, here the agent itself.) The offline
eval above was run with this setting, so container-to-container traffic is unaffected.

### Security options from `docker inspect`

```
$ docker inspect agoe-sandbox-agent-1 --format '...'
user=10001:10001 ro=true capdrop=[ALL] capadd=<no value> secopt=[no-new-privileges:true]
pids=64 mem=268435456 nanocpu=1000000000
tmpfs=map[/tmp:size=16m,mode=1777,noexec,nosuid,nodev] priv=false init=true net=agoe-sandbox_sandbox
bind:.../docker/secrets/agoe_agent_token->/run/secrets/agoe_agent_token rw=false;

$ docker inspect agoe-sandbox-egress-proxy-1 --format '...'
proxy nets=agoe-sandbox_egress agoe-sandbox_sandbox  ro=true capdrop=[ALL] secopt=[no-new-privileges:true]
agent-live nets=agoe-sandbox_sandbox  mounts=/run/secrets/agoe_agent_token /run/secrets/anthropic_api_key
```

### Egress proxy, live-agent profile

External hosts other than a few API endpoints are blocked on this host. So a dummy upstream
(`python3 -m http.server 8443`, alias `upstream.test`) was attached to the egress network
only. Run 1, `EGRESS_ALLOWLIST=upstream.test:8443,api.anthropic.com`, private addresses
refused (default):

```
HTTPS_PROXY = http://egress-proxy:3128
direct https example.com (no proxy) -> FAIL URLError <urlopen error [Errno -3] Temporary failure in name resolution>
via proxy https example.com -> FAIL URLError <urlopen error Tunnel connection failed: 403 host not on allowlist>
via proxy CONNECT upstream.test:8443 (allowlisted, private IP) -> FAIL OSError Tunnel connection failed: 403 destination address not allowed
via proxy CONNECT upstream.test:22 (port not allowlisted) -> FAIL OSError Tunnel connection failed: 403 host not on allowlist
via proxy plain GET http://upstream.test:8443 -> FAIL HTTPError HTTP Error 405: only CONNECT is supported
via proxy https api.anthropic.com (allowlisted) -> FAIL URLError <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] ...
```

The last line is a tunnel the proxy allowed (`"event": "allow", "host": "api.anthropic.com",
"via": "160.79.104.10"`). TLS then failed because this host's own egress proxy intercepts TLS
with a CA the agent image does not trust. That is a property of the test host, not of the
sandbox. Run 2, `EGRESS_ALLOW_PRIVATE=1`, with the host's CA handed to the probe over stdin
for this test only (it is not in any image):

```
CONNECT upstream.test:8443 (allowlisted, ALLOW_PRIVATE=1) -> OK (200, b'<!DOCTYPE HTML>\n<html ')
CONNECT example.com:443 (not allowlisted) -> FAIL OSError Tunnel connection failed: 403 host not on allowlist
https api.anthropic.com via proxy (session CA trusted for this test only) -> OK HTTP 401 from api.anthropic.com (no key sent)
agent /start without bearer token -> OK HTTP 401
```

Proxy log for run 2:

```
{"allow_private": true, "allowlist": ["upstream.test:8443", "api.anthropic.com:443"], "event": "start", ...}
{"event": "allow", "host": "upstream.test", "peer": "172.18.0.2", "port": 8443, "via": "172.19.0.3", ...}
{"event": "deny", "host": "example.com", "peer": "172.18.0.2", "port": 443, "reason": "not_allowlisted", ...}
{"event": "allow", "host": "api.anthropic.com", "peer": "172.18.0.2", "port": 443, "via": "160.79.104.10", ...}
```

`make eval PROFILE=live-agent` then gave `{"completed":26,"errors":0,...}`.

### Build CA not in the image

The CA bundle used for the build holds 123 certificates. Sixteen are absent from the image's
system store. Ten of those are public roots also shipped in pip's vendored certifi (pip has
since been removed). The other six are specific to the test host's proxy.
`grep -rlF` of a line from each of the six over the whole harness filesystem found nothing.
The final image's history has no layer from the `npm ci` step, which runs in the discarded
build stage.

## What Docker does not isolate

These containers are a process sandbox on a shared kernel. They are suited to agents you
expect to behave and want to keep from reaching the network or the host by accident. They
are not a boundary against an agent that is actively trying to escape.

- **Shared kernel.** Every container makes syscalls into the host kernel. A kernel or runc
  vulnerability can give a container root on the host. Docker's default seccomp profile and
  AppArmor (where enabled) reduce the reachable surface; they do not remove it. For hostile or
  untrusted agent code, run the agent container under a stronger runtime: gVisor (`runsc`,
  user-space kernel; add `runtime: runsc` to the agent service once it is installed), Kata
  Containers (lightweight VM per container), or a Firecracker microVM. Not tested here; this
  host's Docker has only `runc`.
- **Root daemon.** With rootful Docker, anyone who can talk to the Docker socket is root on
  the host, and a container escape lands as root. Rootless Docker (or Podman rootless) maps
  container root to an unprivileged host user. In rootless mode, `RESULTS_UID` and bind-mount
  ownership map differently; check the owner of the results directory after the first run.
- **Covert channels through allowed paths.** Anything the agent can send to an allowlisted
  host (including its model provider) can carry data. The proxy limits where traffic goes,
  not what it says.
- **Side channels and resource contention.** CPU caches, timing and shared memory bandwidth
  are not partitioned. The limits stop fork bombs and memory exhaustion from taking the host
  down; they do not hide host activity.
- **Harness trust.** The harness talks to the agent and parses its replies. A malformed or
  oversized reply is bounded by the runner (1 MiB, schema checks), but a bug in that code is
  reachable from the agent. `--agent-cmd` runs the agent inside the harness container, with
  the harness's access to `/out`. Use the HTTP transport and a separate container for agents
  you do not trust.
- **IPv6.** The compose networks do not enable IPv6. If your daemon enables IPv6 by default
  (`default-network-opts` or `ip6tables`), check that the sandbox network gets no IPv6 route.
- **Host firewall.** The isolation relies on Docker's iptables/nftables rules. A host firewall
  manager that flushes those rules (some `firewalld`/`ufw` setups) can remove it. Re-run the
  probes above after changing host networking.

## Gaps

- Not exercised here: gVisor/Kata runtimes, rootless Docker, arm64 builds, and a real model
  call with a valid key through the proxy (the 401 above shows the tunnel and TLS path work).
- `make build` with the default `REGISTRY=docker.io/library` was rate limited (429) on this
  host. The digests are the same through `mirror.gcr.io/library`.
