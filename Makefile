# Docker sandbox targets. See docs/SANDBOX.md.
#
#   make build          build harness, agent-sandbox and egress-proxy images
#   make test-offline   offline mock eval in the harness image (--network none) -> $(OFFLINE_OUT)
#   make sandbox-up     start the agent (and the egress proxy for PROFILE=live-agent)
#   make eval           run the harness against the agent via compose -> $(RESULTS_DIR)/$(RUN)
#   make sandbox-down   stop and remove the sandbox containers and networks
#   make clean          sandbox-down, remove the images built here and local results
#
# Variables (override on the command line):
#   PROFILE=offline|live-agent   EGRESS_ALLOWLIST=api.anthropic.com   STAGE=smoke
#   AGENT_NAME=...   RUN=<subdir>   REGISTRY=mirror.gcr.io/library (pull the pinned digests via a mirror)
#   CA_BUNDLE=/path/ca.pem   proxy CA for npm ci, passed as a BuildKit secret (not stored in the image)
#   BUILD_FLAGS=--network=host   extra docker build flags

SHELL        := /bin/sh
VERSION      ?= dev
REGISTRY     ?= docker.io/library
PROFILE      ?= offline
STAGE        ?= smoke
AGENT_NAME   ?= reference-http-agent
RUN          ?= $(PROFILE)-$(shell date -u +%Y%m%dT%H%M%SZ)
RESULTS_DIR  ?= $(CURDIR)/docker/results
OFFLINE_OUT  ?= $(RESULTS_DIR)/offline-mock
CA_BUNDLE    ?=
BUILD_FLAGS  ?=
EGRESS_ALLOWLIST ?= api.anthropic.com

HARNESS_IMAGE := agoe-harness:$(VERSION)
AGENT_IMAGE   := agoe-agent-sandbox:$(VERSION)
PROXY_IMAGE   := agoe-egress-proxy:$(VERSION)
REVISION      := $(shell git rev-parse HEAD 2>/dev/null || echo unknown)

# Never run the harness as root: use the caller's UID, or 10001 when the caller is root.
UID_         := $(shell id -u)
GID_         := $(shell id -g)
RESULTS_UID  := $(if $(filter 0,$(UID_)),10001,$(UID_))
RESULTS_GID  := $(if $(filter 0,$(UID_)),10001,$(GID_))
AS_ROOT_CHOWN = $(if $(filter 0,$(UID_)),chown $(RESULTS_UID):$(RESULTS_GID) $(1),true)

comma        := ,
SECRET_FLAG  := $(if $(CA_BUNDLE),--secret id=ca$(comma)src=$(CA_BUNDLE),)
COMPOSE      := REGISTRY=$(REGISTRY) AGOE_VERSION=$(VERSION) STAGE=$(STAGE) AGENT_NAME=$(AGENT_NAME) \
                EGRESS_ALLOWLIST=$(EGRESS_ALLOWLIST) RESULTS_UID=$(RESULTS_UID) RESULTS_GID=$(RESULTS_GID) \
                docker compose --profile $(PROFILE)

HARDEN := --read-only --cap-drop ALL --security-opt no-new-privileges \
          --pids-limit 128 --memory 512m --memory-swap 512m --cpus 1 \
          --tmpfs /tmp:size=16m,noexec,nosuid,nodev --user $(RESULTS_UID):$(RESULTS_GID)

.PHONY: build build-harness build-agent build-proxy test-offline secrets sandbox-up sandbox-down eval clean

build: build-harness build-agent build-proxy

build-harness:
	docker build $(BUILD_FLAGS) $(SECRET_FLAG) --build-arg REGISTRY=$(REGISTRY) \
	  --build-arg VERSION=$(VERSION) --build-arg REVISION=$(REVISION) -t $(HARNESS_IMAGE) .

build-agent:
	docker build $(BUILD_FLAGS) --build-arg REGISTRY=$(REGISTRY) --build-arg VERSION=$(VERSION) \
	  -f docker/agent-sandbox/Dockerfile -t $(AGENT_IMAGE) .

build-proxy:
	docker build $(BUILD_FLAGS) --build-arg REGISTRY=$(REGISTRY) \
	  -f docker/egress-proxy/Dockerfile -t $(PROXY_IMAGE) .

# Offline eval: mock provider, no network at all. Mock costs are notional, hence the budget.
test-offline:
	mkdir -p $(OFFLINE_OUT)
	$(call AS_ROOT_CHOWN,$(OFFLINE_OUT))
	docker run --rm --network none $(HARDEN) -v $(OFFLINE_OUT):/out $(HARNESS_IMAGE) \
	  --stage $(STAGE) --budget-usd 1000
	@test -s $(OFFLINE_OUT)/results.jsonl && \
	  echo "results: $(OFFLINE_OUT)/results.jsonl ($$(wc -l < $(OFFLINE_OUT)/results.jsonl) rows)"

# docker/secrets is 0700 so other host users cannot read it; the files are 0644 because compose
# bind-mounts them unchanged and the containers run as a non-root UID that must read them.
secrets:
	@mkdir -p docker/secrets && chmod 700 docker/secrets
	@test -s docker/secrets/agoe_agent_token || \
	  { python3 -c 'import secrets; print(secrets.token_urlsafe(32))' > docker/secrets/agoe_agent_token; \
	    chmod 644 docker/secrets/agoe_agent_token; echo "created docker/secrets/agoe_agent_token"; }
	@test -e docker/secrets/model_api_key || \
	  { : > docker/secrets/model_api_key; chmod 644 docker/secrets/model_api_key; \
	    echo "created empty docker/secrets/model_api_key (put the agent's model key here for live-agent)"; }

sandbox-up: secrets
	$(COMPOSE) up -d --build --wait $(if $(filter live-agent,$(PROFILE)),agent-live egress-proxy,agent)

eval: secrets
	mkdir -p $(RESULTS_DIR)/$(RUN)
	$(call AS_ROOT_CHOWN,$(RESULTS_DIR)/$(RUN))
	RESULTS_DIR=$(RESULTS_DIR)/$(RUN) $(COMPOSE) run --rm harness
	@echo "results: $(RESULTS_DIR)/$(RUN)"

sandbox-down:
	docker compose --profile offline --profile live-agent down --remove-orphans

# Removes only what this Makefile creates: the three images and docker/results/* (not .gitignore).
clean: sandbox-down
	-docker image rm $(HARNESS_IMAGE) $(AGENT_IMAGE) $(PROXY_IMAGE)
	find docker/results -mindepth 1 -maxdepth 1 ! -name .gitignore -exec rm -rf -- {} +
