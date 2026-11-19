#!/usr/bin/env python3
"""VHDLBits web frontend.

  ./serve.py              serve on http://localhost:8000
  ./serve.py --port 9000
  ./serve.py --host 0.0.0.0   listen on every interface (put auth in front of it)

A thin local UI over the same files the command line uses: it shows each problem's
README, edits the learner files in problems/<id>/, and runs ./check.py on Submit.
The editor opens on the starter code; the last passing solution (.solved/<id>/) and the
last attempt (problems/<id>/) are a click away. Like HDLBits, the reference solution
(solutions/<id>.vhd) is only sent once the problem has passed.
Listens on 127.0.0.1 unless --host says otherwise.
"""
import argparse
import json
import re
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import check

ROOT = check.ROOT
PAGE = ROOT / "frontend" / "index.html"

# Grading reuses build/<id>/, so run one check at a time.
grade_lock = threading.Lock()


def problems_by_id():
    return {p["id"]: p for p in check.load_problems()}


def read_or_none(path):
    return path.read_text() if path.is_file() else None


def file_versions(p, f):
    """The starter code, the working copy on disk, and the last passing solution (or None)."""
    draft = f.read_text()
    return {"name": f.name, "draft": draft,
            "starter": read_or_none(p["dir"] / "starter" / f.name) or draft,
            "solution": read_or_none(check.SOLVED / p["id"] / f.name)}


def reference(p):
    """The reference solution, once the problem has been passed (otherwise None)."""
    if check.load_progress().get(p["id"]) != "pass":
        return None
    return read_or_none(check.SOLUTIONS / f"{p['id']}.vhd")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(n) or b"{}")

    def problem(self, pid):
        p = problems_by_id().get(pid)
        if not p:
            self.send_json({"error": f"no problem {pid}"}, 404)
        return p

    def do_GET(self):
        if self.path in ("/", "/index.html") or self.path.startswith("/#"):
            body = PAGE.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/api/problems":
            prog = check.load_progress()
            self.send_json([
                {"id": p["id"], "section": p["section"], "num": p["num"], "name": p["name"],
                 "section_title": check.SECTION_TITLES.get(p["section"], ""),
                 "status": prog.get(p["id"], "")}
                for p in check.load_problems()
            ])
        elif self.path.startswith("/api/problem/"):
            p = self.problem(self.path.rsplit("/", 1)[1])
            if p:
                self.send_json({
                    "id": p["id"],
                    "readme": (p["dir"] / "README.md").read_text(),
                    "files": [file_versions(p, f) for f in check.editable_files(p)],
                    "reference": reference(p),
                })
        elif self.path.startswith("/api/asset/"):
            pid, _, name = self.path.removeprefix("/api/asset/").partition("/")
            p = problems_by_id().get(pid)
            path = p and re.fullmatch(r"diagram(_\d+)?\.svg", name) and p["dir"] / name
            if not path or not path.is_file():
                self.send_json({"error": "not found"}, 404)
                return
            body = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "image/svg+xml")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_json({"error": "not found"}, 404)

    def save(self, p, files):
        allowed = {f.name: f for f in check.editable_files(p)}
        for name, text in files.items():
            if name not in allowed:
                raise ValueError(f"{name} is not an editable file of {p['id']}")
        for name, text in files.items():
            allowed[name].write_text(text)

    def do_POST(self):
        kind, _, pid = self.path.removeprefix("/api/").partition("/")
        if kind not in ("save", "check"):
            self.send_json({"error": "not found"}, 404)
            return
        p = self.problem(pid)
        if not p:
            return
        try:
            self.save(p, self.read_json().get("files", {}))
        except ValueError as e:
            self.send_json({"error": str(e)}, 400)
            return
        if kind == "save":
            self.send_json({"saved": True})
            return
        with grade_lock:
            r = subprocess.run([sys.executable, str(ROOT / "check.py"), p["id"]],
                               cwd=ROOT, capture_output=True, text=True)
        out = (r.stdout + r.stderr).strip()
        self.send_json({"passed": r.returncode == 0, "output": out,
                        "status": check.load_progress().get(p["id"], ""),
                        "reference": reference(p)})


def main():
    ap = argparse.ArgumentParser(description="VHDLBits web frontend")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--no-browser", action="store_true", help="don't open a browser tab")
    args = ap.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    url = f"http://localhost:{args.port}/"
    print(f"VHDLBits at {url}  (Ctrl+C to stop)")
    if not args.no_browser:
        threading.Timer(0.5, webbrowser.open, [url]).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
