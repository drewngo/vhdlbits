#!/usr/bin/env python3
"""Generate problems/<id>/ folders from the definitions in tools/defs/sNN.py.

  python3 tools/gen.py            write README.md, problem.json, provided/ for every problem;
                                  create top_module.vhd (and extra learner files) only if missing;
                                  pristine copies always go to starter/ (the web UI's Reset)
  python3 tools/gen.py --force    also overwrite learner stubs (destroys learner work!)
  python3 tools/gen.py 3          only section 3

Each defs module exports PROBLEMS, a list of dicts. Keys:
  num, name, concept, intro, verilog, task, ports (spec notation), hints
  mode        "comb" (default) | "seq" | "stateful_comb" | "tb"
  generics    {"W": 6}            stub generic defaults (also used by the grader)
  stub        full custom stub text (entity block is lifted into the README)
  arch_decls  text placed between `architecture ... is` and `begin` in a default stub
  arch_body   text placed after `begin` in a default stub (replaces the placeholder comment)
  numeric     True to add `use ieee.numeric_std.all` to the default stub
  uses        extra use clauses for the default stub, e.g. ["work.my_pkg.all"]
  provided    {"file.vhd": text}  modules the learner instantiates (not edited)
  extra       {"file.vhd": text}  extra learner-editable files (compiled before top_module.vhd)
  options     extra problem.json keys (bias, range, cycles, ...)
  interfaces  (mode "tb") README text describing the provided entities
  mutants     (mode "tb") {"name.vhd": text} buggy designs, written to solutions/mutants/<id>/

Diagrams live apart from the text, in tools/figs/sNN.py: FIGURES maps a problem name to an
SVG string (or a list of them) built with tools/diagrams.py. Each is written next to the
README as diagram.svg (diagram_2.svg, ...) and shown under the task, using the SVG's <title>
as the alt text.
"""
import importlib.util
import json
import re
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFS = Path(__file__).resolve().parent / "defs"
FIGS = Path(__file__).resolve().parent / "figs"
PROBLEMS = ROOT / "problems"

TYPE_MAP = {"sl": "std_logic", "std_logic": "std_logic", "std_ulogic": "std_ulogic",
            "slv": "std_logic_vector", "sulv": "std_ulogic_vector",
            "uns": "unsigned", "sgn": "signed"}


def parse_ports(spec):
    """'a, b: in sl; v: out slv(7:0)' -> list of (names, dir, type, high, low)."""
    groups = []
    for chunk in spec.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        names, rest = chunk.split(":", 1)
        m = re.fullmatch(r"\s*(in|out)\s+(\w+)\s*(?:\((.+):(.+)\))?\s*", rest)
        if not m:
            raise ValueError(f"bad port spec: {chunk}")
        d, t, hi, lo = m.groups()
        typ = TYPE_MAP[t]
        groups.append(([n.strip() for n in names.split(",")], d, typ,
                       hi.strip() if hi else None, lo.strip() if lo else None))
    return groups


def vhdl_type(typ, hi, lo):
    if hi is None:
        return typ
    return f"{typ}({hi} downto {lo})"


def entity_block(pdef):
    groups = parse_ports(pdef["ports"])
    lines = ["entity top_module is"]
    gens = pdef.get("generics")
    if gens:
        gtypes = pdef.get("generic_types", {})
        items = [f"{k} : {gtypes.get(k, 'positive')} := {str(v).lower() if isinstance(v, bool) else v}"
                 for k, v in gens.items()]
        lines.append("  generic (")
        lines.append(";\n".join(f"    {i}" for i in items))
        lines.append("  );")
    lines.append("  port (")
    width = max(len(", ".join(n)) for n, *_ in groups)
    plines = []
    for names, d, typ, hi, lo in groups:
        plines.append(f"    {', '.join(names):<{width}} : {d:<3} {vhdl_type(typ, hi, lo)}")
    lines.append(";\n".join(plines))
    lines.append("  );")
    lines.append("end entity top_module;")
    return "\n".join(lines)


def default_stub(pdef):
    groups = parse_ports(pdef["ports"])
    numeric = pdef.get("numeric") or any(t in ("unsigned", "signed") for _, _, t, *_ in groups)
    out = ["library ieee;", "use ieee.std_logic_1164.all;"]
    if numeric:
        out.append("use ieee.numeric_std.all;")
    out += [f"use {u};" for u in pdef.get("uses", [])]
    out += ["", entity_block(pdef), "", "architecture rtl of top_module is"]
    if pdef.get("arch_decls"):
        out.append(textwrap.indent(textwrap.dedent(pdef["arch_decls"]).strip("\n"), "  "))
    out.append("begin")
    if pdef.get("arch_body"):
        out.append(textwrap.indent(textwrap.dedent(pdef["arch_body"]).strip("\n"), "  "))
    else:
        out.append("  -- Write your code here")
    out.append("end architecture rtl;")
    return "\n".join(out) + "\n"


def stub_entity_text(stub):
    m = re.search(r"^entity\s+top_module\s+is.*?^end\b[^;]*;", stub, re.S | re.M | re.I)
    if not m:
        raise ValueError("custom stub has no top_module entity")
    return m.group(0)


def json_ports(pdef):
    ports = []
    for names, d, typ, hi, lo in parse_ports(pdef["ports"]):
        for n in names:
            e = {"name": n, "dir": d, "type": typ}
            if hi is not None:
                e["high"] = int(hi) if re.fullmatch(r"\d+", hi) else hi
                e["low"] = int(lo) if re.fullmatch(r"\d+", lo) else lo
            ports.append(e)
    return ports


def problem_json(sec, pdef):
    mode = pdef.get("mode", "comb")
    if mode == "tb":
        pj = {"id": pid(sec, pdef), "section": sec, "num": pdef["num"], "name": pdef["name"], "mode": mode}
        pj.update(pdef.get("options", {}))
        return pj
    names = [p["name"] for p in json_ports(pdef)]
    pj = {"id": pid(sec, pdef), "section": sec, "num": pdef["num"], "name": pdef["name"],
          "mode": mode, "ports": json_ports(pdef)}
    if mode == "seq":
        pj["clock"] = pdef.get("clock", "clk")
        reset = pdef.get("reset", "auto")
        if reset == "auto":
            reset = next((n for n in ("reset", "areset", "resetn", "aresetn") if n in names), None)
        if reset:
            pj["reset"] = {"name": reset, "active": "0" if reset.endswith("n") else "1"}
    if pdef.get("generics"):
        pj["generics"] = pdef["generics"]
    if pdef.get("extra"):
        pj["extra_files"] = list(pdef["extra"])
    pj.update(pdef.get("options", {}))
    return pj


def pid(sec, pdef):
    return f"{sec:02d}_{pdef['num']:02d}_{pdef['name']}"


def md(text):
    return textwrap.dedent(text).strip("\n")


def diagram_names(svgs):
    return ["diagram.svg" if i == 0 else f"diagram_{i + 1}.svg" for i in range(len(svgs))]


def readme(sec, pdef, stub, svgs=()):
    out = [f"# {sec}.{pdef['num']} {pdef['name']}", ""]
    out.append(f"**New concept:** {pdef['concept']}")
    out.append("")
    if pdef.get("intro"):
        out += [md(pdef["intro"]), ""]
    if pdef.get("verilog"):
        out += [f"**Coming from Verilog:** {md(pdef['verilog'])}", ""]
    out += ["## Task", "", md(pdef["task"]), ""]
    for fname, svg in zip(diagram_names(svgs), svgs):
        alt = re.search(r"<title>(.*?)</title>", svg).group(1)
        out += [f"![{alt}]({fname})", ""]
    if pdef.get("mode") == "tb":
        out += ["## Provided", "", md(pdef["interfaces"]), ""]
    else:
        out += ["## Ports", "", "```vhdl", stub_entity_text(stub), "```", ""]
    if pdef.get("after_ports"):
        out += [md(pdef["after_ports"]), ""]
    hints = pdef.get("hints", [])
    if hints:
        out += ["## Hints", ""]
        for i, h in enumerate(hints, 1):
            out += [f"<details><summary>Hint {i}</summary>", "", md(h), "", "</details>", ""]
    out += ["## Check", "", "```", f"./check.py {sec}.{pdef['num']}", "```", ""]
    return "\n".join(out)


def load_module(path):
    spec = importlib.util.spec_from_file_location(f"{path.parent.name}_{path.stem}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_defs(path):
    mod = load_module(path)
    return mod.SECTION, mod.PROBLEMS


def load_figures(stem):
    """{problem name: [svg, ...]} from tools/figs/<stem>.py (empty if there is none)."""
    path = FIGS / f"{stem}.py"
    if not path.exists():
        return {}
    if str(FIGS.parent) not in sys.path:
        sys.path.insert(0, str(FIGS.parent))         # so figs can `import diagrams`
    figs = load_module(path).FIGURES
    return {k: [v] if isinstance(v, str) else list(v) for k, v in figs.items()}


def main():
    force = "--force" in sys.argv
    only = {int(a) for a in sys.argv[1:] if a.isdigit()}
    for path in sorted(DEFS.glob("s[0-9][0-9].py")):
        sec, probs = load_defs(path)
        if only and sec not in only:
            continue
        figures = load_figures(path.stem)
        unknown = set(figures) - {p["name"] for p in probs}
        if unknown:
            raise ValueError(f"figs/{path.stem}.py: no such problem {sorted(unknown)}")
        for pdef in probs:
            d = PROBLEMS / pid(sec, pdef)
            d.mkdir(parents=True, exist_ok=True)
            stub = pdef.get("stub") or default_stub(pdef)
            stub = md(stub) + "\n"
            svgs = figures.get(pdef["name"], [])
            (d / "README.md").write_text(readme(sec, pdef, stub, svgs))
            for old in d.glob("diagram*.svg"):
                old.unlink()
            for fname, svg in zip(diagram_names(svgs), svgs):
                (d / fname).write_text(svg)
            (d / "problem.json").write_text(json.dumps(problem_json(sec, pdef), indent=2) + "\n")
            learner = {("tb.vhd" if pdef.get("mode") == "tb" else "top_module.vhd"): stub}
            learner.update({k: md(v) + "\n" for k, v in pdef.get("extra", {}).items()})
            (d / "starter").mkdir(exist_ok=True)
            for fname, text in learner.items():
                (d / "starter" / fname).write_text(text)
                if force or not (d / fname).exists():
                    (d / fname).write_text(text)
            if pdef.get("provided"):
                (d / "provided").mkdir(exist_ok=True)
                for fname, text in pdef["provided"].items():
                    (d / "provided" / fname).write_text(md(text) + "\n")
            for fname, text in pdef.get("mutants", {}).items():
                mdir = ROOT / "solutions" / "mutants" / pid(sec, pdef)
                mdir.mkdir(parents=True, exist_ok=True)
                (mdir / fname).write_text(md(text) + "\n")
        print(f"section {sec}: {len(probs)} problems")


if __name__ == "__main__":
    main()
