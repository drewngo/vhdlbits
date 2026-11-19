"""Timing diagrams drawn from a simulation of the reference answer (used by tools/figs/sNN.py).

  ref_wave(p, {"reset": [...], "a": [...]}, title=...)

runs solutions/<id>.vhd through the grader's own testbench with the given inputs (one value
per cycle, applied at the falling edge that starts the cycle) and draws every port with
diagrams.wave(), two slots per cycle like diagrams.clocked(). The figure can't drift from
the answer key, so the README never shows a waveform the grader disagrees with.
Needs GHDL; gen.py calls these figures after writing problem.json.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import check  # noqa: E402
from diagrams import to_row, wave  # noqa: E402


def value_at(pts, t):
    v = pts[0][1]
    for tt, vv in pts:
        if tt <= t:
            v = vv
    return v


def label(bits):
    """Bits -> 0/1 for a single bit, decimal for a vector, None for anything unknown."""
    if any(c not in "01" for c in bits):
        return None
    return int(bits, 2)


def ref_wave(p, inputs, title, note=None, slot=18, outputs=None):
    clock = p["clock"]
    ports = [check.Port(d, p.get("generics", {})) for d in p["ports"]]
    ins = [x for x in ports if x.dir == "in" and x.name != clock]
    n = len(next(iter(inputs.values())))
    if set(inputs) != {x.name for x in ins} or any(len(v) != n for v in inputs.values()):
        raise SystemExit(f"{p['id']}: figure needs {n} values for each of {[x.name for x in ins]}")
    stimulus = [(1, [inputs[x.name][k] for x in ins]) for k in range(n)]
    status, detail = check.grade(p, [check.SOLUTIONS / f"{p['id']}.vhd"], waves=False, tag=".fig",
                                 stimulus=stimulus, wave_pass=n)
    if status != "PASS":
        raise SystemExit(f"{p['id']}: reference didn't run for the figure: {status} {detail}")
    w = check.json.loads((check.BUILD / (p["id"] + ".fig") / "wave.json").read_text())
    period = w["period"]
    rows = [("clk", "".join("01" for _ in range(n)))]
    for s in w["signals"]:
        pts = s["wave"] if s["dir"] == "in" else s["ref"]
        seq = [label(value_at(pts, k * period + h * period / 2 + period / 4)) for k in range(n) for h in (0, 1)]
        rows.append(to_row(s["name"], seq))
    outs = outputs or tuple(s["name"] for s in w["signals"] if s["dir"] == "out")
    return wave(rows, slot=slot, outputs=outs, title=title, note=note)
