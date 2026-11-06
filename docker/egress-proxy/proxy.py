#!/usr/bin/env python3
"""Allowlisting HTTPS forward proxy (CONNECT only), Python stdlib.

The agent under test sits on a network with no route out. This proxy is the only
container attached to both that network and an egress network, and it opens a TCP
tunnel only to hosts on EGRESS_ALLOWLIST. It does not terminate TLS: it sees the
host name and port of each CONNECT, never the request contents or API keys.

Environment:
  EGRESS_ALLOWLIST   comma-separated entries: "host", "host:port" or ".suffix" (matches
                     subdomains of suffix, not suffix itself). Port defaults to 443.
                     Empty list = deny everything.
  LISTEN             bind address, default 0.0.0.0:3128
  ALLOW_PRIVATE      "1" to allow allowlisted hosts that resolve to loopback, private,
                     link-local or other non-global addresses (default: refused, so a
                     DNS answer cannot point the tunnel at cloud metadata or the host).
  UPSTREAM_PROXY     optional http://host:port of a parent proxy; allowed CONNECTs are
                     chained through it (for networks that only egress via a proxy).
  MAX_CONNS          concurrent tunnels, default 64
  IDLE_TIMEOUT       seconds without traffic before a tunnel is closed, default 120

Every decision is logged to stdout as one JSON line.
"""

import ipaddress
import json
import os
import select
import socket
import socketserver
import sys
import threading
import time
import urllib.parse

MAX_HEADER = 8192


def log(**kv):
    kv["ts"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    sys.stdout.write(json.dumps(kv, sort_keys=True) + "\n")
    sys.stdout.flush()


def parse_allowlist(raw):
    entries = []
    for item in (raw or "").split(","):
        item = item.strip().lower()
        if not item:
            continue
        host, _, port = item.rpartition(":") if item.count(":") == 1 else (item, "", "")
        if not host:
            host, port = item, ""
        entries.append((host.rstrip("."), int(port) if port else 443))
    return entries


def allowed(entries, host, port):
    host = host.lower().rstrip(".")
    for h, p in entries:
        if p != port:
            continue
        if h.startswith("."):
            if host.endswith(h) and host != h[1:]:
                return True
        elif host == h:
            return True
    return False


def resolve_checked(host, port, allow_private):
    """Resolve once and return a public address; connecting to this exact address
    (not the name again) closes the DNS-rebinding window between check and use."""
    infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    for family, _, _, _, addr in infos:
        ip = ipaddress.ip_address(addr[0])
        if allow_private or ip.is_global:
            return family, addr
    raise PermissionError("resolves only to non-global addresses")


class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        cfg = self.server.cfg
        peer = self.client_address[0]
        if not cfg["slots"].acquire(blocking=False):
            self.reply(503, "too many tunnels")
            log(event="deny", peer=peer, reason="max_conns")
            return
        try:
            self._handle(cfg, peer)
        finally:
            cfg["slots"].release()

    def reply(self, code, text):
        try:
            self.request.sendall(f"HTTP/1.1 {code} {text}\r\nContent-Length: 0\r\nConnection: close\r\n\r\n".encode())
        except OSError:
            pass

    def _handle(self, cfg, peer):
        self.request.settimeout(15)
        buf = b""
        try:
            while b"\r\n\r\n" not in buf:
                chunk = self.request.recv(1024)
                if not chunk:
                    return
                buf += chunk
                if len(buf) > MAX_HEADER:
                    self.reply(431, "header too large")
                    return
        except OSError:
            return
        head, _, rest = buf.partition(b"\r\n\r\n")
        try:
            method, target, _ = head.split(b"\r\n", 1)[0].decode("latin-1").split(" ", 2)
        except ValueError:
            self.reply(400, "bad request")
            return
        if method.upper() != "CONNECT":
            # Plain-HTTP forwarding would let the proxy see and forward cleartext bodies;
            # model APIs are HTTPS, so only tunnels are offered.
            self.reply(405, "only CONNECT is supported")
            log(event="deny", peer=peer, method=method, reason="method")
            return
        host, sep, port_s = target.rpartition(":")
        host = host.strip("[]")
        if not sep or not port_s.isdigit() or not host:
            self.reply(400, "bad CONNECT target")
            return
        port = int(port_s)
        if not allowed(cfg["allow"], host, port):
            self.reply(403, "host not on allowlist")
            log(event="deny", peer=peer, host=host, port=port, reason="not_allowlisted")
            return
        try:
            if cfg["upstream"]:
                up = socket.create_connection(cfg["upstream"], timeout=15)
                up.sendall(f"CONNECT {host}:{port} HTTP/1.1\r\nHost: {host}:{port}\r\n\r\n".encode())
                resp = b""
                while b"\r\n\r\n" not in resp and len(resp) < MAX_HEADER:
                    chunk = up.recv(1024)
                    if not chunk:
                        break
                    resp += chunk
                status = resp.split(b" ", 2)[1:2]
                if status != [b"200"]:
                    up.close()
                    raise ConnectionError(f"upstream proxy answered {resp[:40]!r}")
                where = "upstream"
            else:
                family, addr = resolve_checked(host, port, cfg["allow_private"])
                up = socket.socket(family, socket.SOCK_STREAM)
                up.settimeout(15)
                up.connect(addr)
                where = addr[0]
        except PermissionError as e:
            self.reply(403, "destination address not allowed")
            log(event="deny", peer=peer, host=host, port=port, reason=str(e))
            return
        except (OSError, ConnectionError) as e:
            self.reply(502, "upstream connect failed")
            log(event="error", peer=peer, host=host, port=port, reason=type(e).__name__)
            return
        log(event="allow", peer=peer, host=host, port=port, via=where)
        self.request.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
        if rest:
            up.sendall(rest)
        self.pipe(self.request, up, cfg["idle"])

    @staticmethod
    def pipe(a, b, idle):
        a.setblocking(False)
        b.setblocking(False)
        socks = [a, b]
        try:
            while True:
                r, _, _ = select.select(socks, [], [], idle)
                if not r:
                    return
                for s in r:
                    data = s.recv(65536)
                    if not data:
                        return
                    (b if s is a else a).sendall(data)
        except OSError:
            return
        finally:
            b.close()


class Server(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True


def main():
    host, _, port = os.environ.get("LISTEN", "0.0.0.0:3128").rpartition(":")
    upstream = None
    if os.environ.get("UPSTREAM_PROXY"):
        u = urllib.parse.urlsplit(os.environ["UPSTREAM_PROXY"])
        upstream = (u.hostname, u.port or 3128)
    cfg = {
        "allow": parse_allowlist(os.environ.get("EGRESS_ALLOWLIST", "")),
        "allow_private": os.environ.get("ALLOW_PRIVATE") == "1",
        "upstream": upstream,
        "slots": threading.BoundedSemaphore(int(os.environ.get("MAX_CONNS", "64"))),
        "idle": float(os.environ.get("IDLE_TIMEOUT", "120")),
    }
    srv = Server((host, int(port)), Handler)
    srv.cfg = cfg
    log(event="start", listen=f"{host}:{port}", allowlist=[f"{h}:{p}" for h, p in cfg["allow"]],
        allow_private=cfg["allow_private"], upstream=bool(upstream))
    srv.serve_forever()


if __name__ == "__main__":
    main()
