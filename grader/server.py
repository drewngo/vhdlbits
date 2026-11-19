#!/usr/bin/env python3
"""VHDLBits cloud grader: grades one submission per request, keeps nothing.

  POST /check/<id>   {"files": {"top_module.vhd": "..."}}
                  -> {"status": "PASS", "passed": true, "output": "...", "reference": "..." | null}
  GET  /health

Runs on Cloud Run behind a Cloudflare Worker, which checks Turnstile and forwards the request
with the shared secret in X-Grader-Key and the visitor's address in X-Client-IP.

Submissions are untrusted code, so each one is graded by a child process (this file with
--grade) in a fresh temp directory, as user nobody when we are root, with resource limits and
no secrets in its environment. The service itself has no outbound network and a service
account with no permissions; this process only adds rate limits and cleanup on top of that.

  ./grader/server.py --dev            local testing on http://localhost:8080, no key needed
"""
import argparse
import collections
import contextlib
import hmac
import io
import json
import os
import re
import resource
import shutil
import subprocess
import sys
import tempfile
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import check  # noqa: E402

GRADER_KEY = os.environ.get("GRADER_KEY", "")
STEP_TIMEOUT = int(os.environ.get("STEP_TIMEOUT", 10))       # each ghdl call
GRADE_TIMEOUT = int(os.environ.get("GRADE_TIMEOUT", 25))     # the whole grade
PER_IP_PER_MINUTE = int(os.environ.get("PER_IP_PER_MINUTE", 10))
PER_IP_PER_DAY = int(os.environ.get("PER_IP_PER_DAY", 300))
GLOBAL_PER_DAY = int(os.environ.get("GLOBAL_PER_DAY", 3000))
MAX_BODY = 256 * 1024
MAX_FILE = 64 * 1024
NOBODY = 65534

# VHPIDIRECT (attribute foreign) lets VHDL call any C function, system() included.
FORBIDDEN = re.compile(r"\bforeign\b|vhpi", re.I)


# --------------------------------------------------------------------------
# Child: grade one submission
# --------------------------------------------------------------------------

def grade_one(pid, work):
    """Runs as the sandboxed child. Prints {"status", "output"} as JSON."""
    work = Path(work)
    p = check.find_problem(check.load_problems(), pid)
    check.BUILD = work / "build"
    check.RUN_TIMEOUT = STEP_TIMEOUT
    files = [work / "src" / f.name if (work / "src" / f.name).is_file() else f
             for f in check.learner_files(p)]
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        status, detail = check.grade(p, files, waves=False)
        check.report(p, status, detail)
    text = out.getvalue().replace(f"{work}/src/", "").replace(f"{work}/", "")
    print(json.dumps({"status": status, "output": text.strip()}))


def limit_child():
    resource.setrlimit(resource.RLIMIT_CPU, (GRADE_TIMEOUT, GRADE_TIMEOUT))
    resource.setrlimit(resource.RLIMIT_FSIZE, (32 << 20, 32 << 20))
    resource.setrlimit(resource.RLIMIT_NOFILE, (256, 256))
    if os.getuid() == 0:
        resource.setrlimit(resource.RLIMIT_NPROC, (64, 64))


def grade_submission(p, files):
    work = Path(tempfile.mkdtemp(prefix="grade-"))
    try:
        (work / "src").mkdir()
        for name, text in files.items():
            (work / "src" / name).write_text(text)
        drop = {}
        if os.getuid() == 0:
            for d in (work, *work.rglob("*")):
                os.chown(d, NOBODY, NOBODY)
            drop = {"user": NOBODY, "group": NOBODY, "extra_groups": []}
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(work), "TMPDIR": str(work),
               "STEP_TIMEOUT": str(STEP_TIMEOUT), "GRADE_TIMEOUT": str(GRADE_TIMEOUT)}
        try:
            r = subprocess.run([sys.executable, __file__, "--grade", p["id"], str(work)],
                               cwd=work, env=env, capture_output=True, text=True,
                               timeout=GRADE_TIMEOUT, preexec_fn=limit_child, **drop)
        except subprocess.TimeoutExpired:
            return {"status": "ERROR", "output": f"grading timed out after {GRADE_TIMEOUT} s"}
        finally:
            if drop:  # anything the submission left running as nobody
                subprocess.run(["pkill", "-9", "-u", str(NOBODY)], capture_output=True)
        try:
            return json.loads(r.stdout.strip().splitlines()[-1])
        except (IndexError, ValueError):
            print(f"grader child failed ({r.returncode}): {r.stderr[-2000:]}", file=sys.stderr)
            return {"status": "ERROR", "output": "the grader failed on this submission"}
    finally:
        shutil.rmtree(work, ignore_errors=True)


# --------------------------------------------------------------------------
# Rate limits (one instance, one request at a time, so in-process state is enough)
# --------------------------------------------------------------------------

class Limits:
    def __init__(self):
        self.minute = collections.defaultdict(collections.deque)
        self.day = collections.Counter()
        self.total = 0
        self.today = time.strftime("%Y-%m-%d", time.gmtime())

    def allow(self, ip):
        """None if allowed (and counted), else the reason it isn't."""
        today = time.strftime("%Y-%m-%d", time.gmtime())
        if today != self.today:
            self.__init__()
        now = time.monotonic()
        recent = self.minute[ip]
        while recent and now - recent[0] > 60:
            recent.popleft()
        if self.total >= GLOBAL_PER_DAY:
            return "The grader has hit its daily limit. Try again tomorrow (UTC)."
        if self.day[ip] >= PER_IP_PER_DAY:
            return "You've hit today's check limit. Try again tomorrow (UTC)."
        if len(recent) >= PER_IP_PER_MINUTE:
            return "Too many checks in the last minute. Wait a moment and try again."
        recent.append(now)
        self.day[ip] += 1
        self.total += 1
        return None


limits = Limits()
PROBLEMS = {p["id"]: p for p in check.load_problems()}


class Handler(BaseHTTPRequestHandler):
    dev = False

    def log_message(self, fmt, *args):
        pass

    def send_json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self.send_json({"ok": True})
        else:
            self.send_json({"error": "not found"}, 404)

    def do_POST(self):
        if not self.dev and not (GRADER_KEY and hmac.compare_digest(
                self.headers.get("X-Grader-Key", ""), GRADER_KEY)):
            self.send_json({"error": "forbidden"}, 403)
            return
        p = PROBLEMS.get(self.path.removeprefix("/check/"))
        if not self.path.startswith("/check/") or not p:
            self.send_json({"error": "no such problem"}, 404)
            return
        n = int(self.headers.get("Content-Length", 0))
        if n > MAX_BODY:
            self.send_json({"error": "submission too large"}, 413)
            return
        try:
            files = json.loads(self.rfile.read(n) or b"{}").get("files", {})
        except (ValueError, AttributeError):
            self.send_json({"error": "bad request"}, 400)
            return
        allowed = {f.name for f in check.editable_files(p)}
        if not isinstance(files, dict) or not files or not set(files) <= allowed \
                or not all(isinstance(t, str) and len(t) <= MAX_FILE for t in files.values()):
            self.send_json({"error": f"expected files: {', '.join(sorted(allowed))}"}, 400)
            return
        if any(FORBIDDEN.search(t) for t in files.values()):
            self.send_json({"status": "COMPILE", "passed": False, "reference": None,
                            "output": "The online grader doesn't allow the `foreign` attribute or VHPI. "
                                      "Run ./check.py locally to use them."})
            return
        reason = limits.allow(self.headers.get("X-Client-IP") or self.client_address[0])
        if reason:
            self.send_json({"error": reason}, 429)
            return
        t0 = time.monotonic()
        res = grade_submission(p, files)
        passed = res["status"] == "PASS"
        print(json.dumps({"problem": p["id"], "status": res["status"],
                          "seconds": round(time.monotonic() - t0, 2)}), flush=True)
        self.send_json({**res, "passed": passed,
                        "reference": (check.SOLUTIONS / f"{p['id']}.vhd").read_text() if passed else None})


def main():
    if len(sys.argv) == 4 and sys.argv[1] == "--grade":
        grade_one(sys.argv[2], sys.argv[3])
        return
    ap = argparse.ArgumentParser(description="VHDLBits cloud grader")
    ap.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8080)))
    ap.add_argument("--dev", action="store_true", help="listen on localhost and skip the key check")
    args = ap.parse_args()
    if not args.dev and not GRADER_KEY:
        raise SystemExit("GRADER_KEY is not set (use --dev for local testing)")
    Handler.dev = args.dev
    host = "127.0.0.1" if args.dev else "0.0.0.0"
    print(f"grader on {host}:{args.port}, {len(PROBLEMS)} problems", flush=True)
    HTTPServer((host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
