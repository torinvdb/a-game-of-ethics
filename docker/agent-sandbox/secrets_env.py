#!/usr/bin/env python3
"""Load Docker/Compose secrets into the environment, then exec the agent.

Each regular file /run/secrets/<name> becomes the variable <NAME> (upper-cased, with
non-alphanumerics turned into "_") unless that variable is already set. Values never
appear in `docker inspect` or the compose file, only in this process tree.

  python3 -I secrets_env.py -- python3 -I http_agent.py --host 0.0.0.0 --port 8080
"""
import os
import re
import sys

SECRETS = os.environ.get("SECRETS_DIR", "/run/secrets")


def main(argv):
    if argv[:1] == ["--"]:
        argv = argv[1:]
    if not argv:
        sys.exit("usage: secrets_env.py -- CMD [ARGS...]")
    if os.path.isdir(SECRETS):
        for name in sorted(os.listdir(SECRETS)):
            path = os.path.join(SECRETS, name)
            if not os.path.isfile(path):
                continue
            var = re.sub(r"[^A-Za-z0-9]", "_", name).upper()
            if var in os.environ:
                continue
            with open(path, encoding="utf-8") as f:
                os.environ[var] = f.read().strip()
    os.execvp(argv[0], argv)


if __name__ == "__main__":
    main(sys.argv[1:])
