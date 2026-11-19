#!/usr/bin/env python3
"""Check the reference answers against independent Python models.

  python3 tools/verify_refs.py          every problem that has a model
  python3 tools/verify_refs.py 3 4.5    section 3 and problem 4.5

The grader only proves that a learner matches solutions/<id>.vhd, so a wrong
reference silently becomes a wrong answer key. This script simulates each
reference with the grader's own stimulus (trace enabled), then replays the
same inputs through a model in tools/models/sNN.py and compares every sample.

Models (MODELS dict, keyed by problem name):
  comb           f(i) -> {out: value}
  stateful_comb  class with step(i) -> {out: value}
  seq            class with out(i) -> {out: value}, clk(i), optional fall(i)
                 (out() sees the current state; async resets belong in out()/clk())
`i` maps each input name to an int (std_logic is 0/1). Output values may be
ints, exact strings such as 'Z', or None to skip that output for this sample.
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(ROOT))
import check  # noqa: E402

MAX_REPORT = 8


def load_models():
    models = {}
    for path in sorted((TOOLS / "models").glob("s[0-9][0-9].py")):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        models.update(mod.MODELS)
    return models


def expect(val, width):
    if val is None or isinstance(val, str):
        return val
    return format(val & ((1 << width) - 1), f"0{width}b")


def verify(p, model):
    ref = check.SOLUTIONS / f"{p['id']}.vhd"
    status, detail = check.grade(p, [ref], waves=False, trace=True, tag=".verify")
    if status != "PASS":
        check.report(p, status, detail)
        return ["reference does not run cleanly"]
    bdir = check.BUILD / (p["id"] + ".verify")
    generics = dict(p.get("generics", {}))
    ports = [check.Port(d, generics) for d in p["ports"]]
    clock = p.get("clock")
    ins = [x for x in ports if x.dir == "in" and x.name != clock]
    outs = [x for x in ports if x.dir == "out"]
    stim = []
    for line in (bdir / "stim.txt").read_text().split("\n"):
        if line.strip():
            f = line.split()
            stim.append((f[0] == "1", {x.name: int(v, 2) for x, v in zip(ins, f[1:])}))
    trace = [l.split() for l in (bdir / "trace.txt").read_text().splitlines() if l.strip()]

    errors = []
    checked = 0

    def compare(t, inputs, got):
        nonlocal checked
        ph, en, vals = t[0], t[1] == "1", t[2:]
        if not en:
            return
        for x, actual in zip(outs, vals):
            want = expect(got.get(x.name), x.width)
            if want is None:
                continue
            checked += 1
            if want != actual:
                errors.append(f"sample {ph} inputs {inputs}: {x.name} model {want} ref {actual}")

    mode = p["mode"]
    if mode == "comb":
        for t, (_, i) in zip(trace, stim):
            compare(t, i, model(i))
    elif mode == "stateful_comb":
        m = model()
        for t, (_, i) in zip(trace, stim):
            compare(t, i, m.step(i))
    elif mode == "seq":
        m = model()
        it = iter(trace)
        prev = None
        for k, (_, i) in enumerate(stim):
            if k > 0:
                compare(next(it), prev, m.out(prev))
                if hasattr(m, "fall"):
                    m.fall(prev)
            compare(next(it), i, m.out(i))
            m.clk(i)
            prev = i
        compare(next(it), prev, m.out(prev))
    if checked == 0:
        errors.append("no samples were checked (model returns None everywhere?)")
    return errors


def main():
    probs = check.load_problems()
    models = load_models()
    sel = probs
    if len(sys.argv) > 1:
        sel = []
        for key in sys.argv[1:]:
            if re.fullmatch(r"\d+", key):
                sel += [p for p in probs if p["section"] == int(key)]
            else:
                sel.append(check.find_problem(probs, key))
    bad = missing = 0
    for p in sel:
        tag = f"{p['section']:>2}.{p['num']:<3} {p['name']}"
        model = models.get(p["name"])
        if model is None:
            if p["mode"] != "tb":
                print(f"--   {tag}: no model")
                missing += 1
            continue
        errs = verify(p, model)
        if errs:
            bad += 1
            print(f"BAD  {tag}: {len(errs)} disagreements")
            for e in errs[:MAX_REPORT]:
                print(f"       {e}")
        else:
            print(f"ok   {tag}")
    print(f"\n{bad} disagreeing, {missing} without a model")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
