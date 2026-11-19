#!/usr/bin/env python3
"""VHDLBits grader.

Usage:
  ./check.py 3.4              grade one problem (by number, name, or folder id)
  ./check.py byte_swap
  ./check.py --list           show every problem with progress
  ./check.py 4.13 -g W=10     override a generic for this run
  ./check.py --selftest [..]  maintainer check: reference vs. itself, stubs compile

The learner's design and the reference answer are compiled into separate
libraries (`dut` and `ref`), both with entity `top_module`. A generated
testbench drives both with identical stimulus and compares every output.
"""
import argparse
import json
import os
import random
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROBLEMS = ROOT / "problems"
SOLUTIONS = ROOT / "solutions"
MUTANTS = SOLUTIONS / "mutants"
BUILD = ROOT / "build"
PROGRESS = ROOT / ".progress.json"
SOLVED = ROOT / ".solved"          # .solved/<id>/: the learner files from the last passing check

GHDL_STD = "--std=08"
MAX_SHOWN = 10
COMB_EXHAUSTIVE_BITS = 12
COMB_RANDOM_VECTORS = 1000
SEQ_DEFAULT_CYCLES = 300
STATEFUL_DEFAULT_STEPS = 500
DEFAULT_RESET_PROB = 0.05
RUN_TIMEOUT = 600
CLOCK_PERIOD = 10                  # ns, set by the generated testbench
# Waveform window, in cycles (vectors for combinational problems): the start of a passing
# run, or this much either side of the first mismatch.
WAVE_PASS, WAVE_BEFORE, WAVE_AFTER = 24, 12, 8

SECTION_TITLES = {
    1: "Getting Started", 2: "Language Basics", 3: "Vectors",
    4: "Hierarchy", 5: "Processes", 6: "Types & numeric_std",
    7: "Combinational Circuits", 8: "Sequential Basics", 9: "Counters",
    10: "Shift Registers & Automata", 11: "Finite State Machines",
    12: "Memories", 13: "Packages, Records & Types",
    14: "Writing Testbenches", 15: "Bigger Builds", 16: "Bug Hunts",
}

VERILOG_HINTS = [
    (r"\d+'[bBhHdDoO]", "Verilog sized literals like 1'b1 or 8'hFF don't exist. Use '1' for a bit, \"0101\" or x\"FF\" for vectors."),
    (r"\bassign\b", "There is no `assign` in VHDL. A concurrent assignment is just `y <= expr;` in the architecture body."),
    (r"\balways\b", "There is no `always` block. Use `process(all)` for combinational logic or `process(clk)` with `if rising_edge(clk)`."),
    (r"\bmodule\b", "VHDL uses `entity` (the interface) plus `architecture` (the body) instead of `module`."),
    (r"\b(wire|reg)\b", "VHDL has no wire/reg. Internal nets are `signal`s declared between `architecture ... is` and `begin`."),
    (r"==", "Equality is `=` in VHDL (and inequality is `/=`)."),
    (r"!=", "Inequality is `/=` in VHDL."),
    (r"&&|\|\|", "VHDL has no `&&`/`||`. Use the keywords `and`/`or`; `&` is concatenation."),
    (r"(?<![<>=/:])=(?!>)\s*[^=]", None),  # placeholder, filtered below
    (r"\bposedge\b|\bnegedge\b", "Clock edges are tested with `rising_edge(clk)` / `falling_edge(clk)` inside a process."),
    (r"(?<![\w'])~\w", "Bitwise NOT is the keyword `not`, not `~`."),
    (r"\?\s*[\w'\"(]+\s*:", "There is no `? :` operator. Use `y <= a when sel = '1' else b;`."),
]
VERILOG_HINTS = [h for h in VERILOG_HINTS if h[1]]


# --------------------------------------------------------------------------
# Problem discovery
# --------------------------------------------------------------------------

def load_problems():
    probs = []
    if not PROBLEMS.is_dir():
        return probs
    for d in sorted(PROBLEMS.iterdir()):
        pj = d / "problem.json"
        if pj.is_file():
            p = json.loads(pj.read_text())
            p["dir"] = d
            probs.append(p)
    return probs


def find_problem(probs, key):
    key = key.strip().rstrip("/")
    m = re.fullmatch(r"(\d+)\.(\d+)", key)
    for p in probs:
        if m and p["section"] == int(m.group(1)) and p["num"] == int(m.group(2)):
            return p
        if key in (p["name"], p["id"]) or Path(key).name == p["id"]:
            return p
    return None


def load_progress():
    try:
        return json.loads(PROGRESS.read_text())
    except (OSError, ValueError):
        return {}


def save_progress(prog):
    PROGRESS.write_text(json.dumps(prog, indent=2, sort_keys=True) + "\n")


def save_solution(p):
    d = SOLVED / p["id"]
    d.mkdir(parents=True, exist_ok=True)
    for f in learner_files(p):
        shutil.copyfile(f, d / f.name)


# --------------------------------------------------------------------------
# Ports
# --------------------------------------------------------------------------

SCALAR_TYPES = ("std_logic", "std_ulogic")
VECTOR_TYPES = ("std_logic_vector", "std_ulogic_vector", "unsigned", "signed")


class Port:
    def __init__(self, d, generics):
        self.name = d["name"]
        self.dir = d["dir"]
        self.type = d["type"]
        if self.type in SCALAR_TYPES:
            self.width = 1
            self.scalar = True
        elif self.type in VECTOR_TYPES:
            hi = ev(d["high"], generics)
            lo = ev(d.get("low", 0), generics)
            self.width = hi - lo + 1
            self.scalar = False
        else:
            raise SystemExit(f"unsupported port type {self.type} on {self.name}")

    def vtype(self):
        if self.scalar:
            return self.type
        return f"{self.type}({self.width - 1} downto 0)"

    def to_slv(self, expr):
        """VHDL expression converting a signal of this port's type to std_logic_vector."""
        if self.scalar:
            return f"std_logic_vector'(0 => {expr})"
        if self.type == "std_logic_vector":
            return expr
        return f"std_logic_vector({expr})"

    def from_slv(self, expr):
        if self.scalar:
            return f"{expr}(0)"
        if self.type == "std_logic_vector":
            return expr
        return f"{self.type}({expr})"


def ev(x, generics):
    if isinstance(x, int):
        return x
    return int(eval(str(x), {"__builtins__": {}}, dict(generics)))


# --------------------------------------------------------------------------
# Stimulus
# --------------------------------------------------------------------------

def expr_env(ins, values):
    env = {"popcount": lambda v: bin(v).count("1"), "onehot": lambda v: v != 0 and v & (v - 1) == 0}
    for port, v in zip(ins, values):
        env[port.name] = v
    return env


def check_expr(expr, ins, values):
    return bool(eval(expr, {"__builtins__": {}}, expr_env(ins, values)))


class Stim:
    def __init__(self, p, ins, rng):
        self.p = p
        self.ins = ins
        self.rng = rng
        self.bias = p.get("bias", {})
        self.value_bias = p.get("value_bias", {})
        self.range = p.get("range", {})
        self.nibble_range = p.get("nibble_range", {})
        self.exclusive = p.get("exclusive", [])
        self.valid = p.get("valid_inputs")
        self.copy = p.get("copy", [])

    def value(self, port):
        r = self.rng
        for val, prob in self.value_bias.get(port.name, []):
            if r.random() < prob:
                return int(val, 16) if isinstance(val, str) else val
        if port.name in self.range:
            lo, hi = self.range[port.name]
            return r.randint(lo, hi)
        if port.name in self.nibble_range:
            lo, hi = self.nibble_range[port.name]
            v = 0
            for i in range(port.width // 4):
                v |= r.randint(lo, hi) << (4 * i)
            return v
        if port.name in self.bias:
            b = self.bias[port.name]
            if port.width == 1:
                return int(r.random() < b)
            return sum(int(r.random() < b) << i for i in range(port.width))
        return r.getrandbits(port.width)

    def fix_exclusive(self, vals):
        idx = {p.name: i for i, p in enumerate(self.ins)}
        for group in self.exclusive:
            hot = [n for n in group if vals[idx[n]]]
            if len(hot) > 1:
                keep = self.rng.choice(hot)
                for n in hot:
                    if n != keep:
                        vals[idx[n]] = 0
        return vals

    def vector(self):
        for _ in range(1000):
            vals = self.fix_exclusive([self.value(port) for port in self.ins])
            idx = {port.name: i for i, port in enumerate(self.ins)}
            for dst, src, prob in self.copy:
                if self.rng.random() < prob:
                    vals[idx[dst]] = vals[idx[src]]
            if not self.valid or check_expr(self.valid, self.ins, vals):
                return vals
        raise SystemExit("valid_inputs filter rejected 1000 random vectors in a row")

    def allowed(self, vals):
        for i, port in enumerate(self.ins):
            if port.name in self.range:
                lo, hi = self.range[port.name]
                if not lo <= vals[i] <= hi:
                    return False
            if port.name in self.nibble_range:
                lo, hi = self.nibble_range[port.name]
                if any(not lo <= (vals[i] >> (4 * k)) & 15 <= hi for k in range(port.width // 4)):
                    return False
        for group in self.exclusive:
            idx = {p.name: i for i, p in enumerate(self.ins)}
            if sum(1 for n in group if vals[idx[n]]) > 1:
                return False
        return not self.valid or check_expr(self.valid, self.ins, vals)


def plugin_uart_frames(rng, n, p, opts):
    """Mix of idle line, well-formed frames, bad frames and noise on one port."""
    bits = []
    parity = opts.get("parity")
    while len(bits) < n:
        kind = rng.random()
        bits += [1] * rng.randint(0, 4)
        if kind < 0.7:
            byte = rng.getrandbits(8)
            frame = [0] + [(byte >> i) & 1 for i in range(8)]
            if parity == "odd":
                pbit = 1 - bin(byte).count("1") % 2
                if rng.random() < 0.15:
                    pbit ^= 1
                frame.append(pbit)
            frame.append(0 if rng.random() < 0.15 else 1)
            bits += frame
        else:
            bits += [int(rng.random() < 0.7) for _ in range(rng.randint(1, 12))]
    return {opts.get("port", "rxd"): bits[:n]}


RV32I_OPCODES = [0x03, 0x13, 0x17, 0x23, 0x33, 0x37, 0x63, 0x67, 0x6F]


def plugin_rv32i(rng, n, p, opts):
    vals = []
    for _ in range(n):
        v = rng.getrandbits(32)
        if rng.random() < 0.9:
            v = (v & ~0x7F) | rng.choice(RV32I_OPCODES)
            if rng.random() < 0.7:
                v = (v & 0x01FFFFFF) | (rng.choice([0x00, 0x20]) << 25)
        vals.append(v)
    return {opts.get("port", "instr"): vals}


def plugin_runs(rng, n, p, opts):
    """A 1-bit input that holds each level for a random run length (bouncy buttons)."""
    bits, level = [], 0
    while len(bits) < n:
        bits += [level] * rng.randint(opts.get("min", 1), opts.get("max", 20))
        level ^= 1
    return {opts["port"]: bits[:n]}


PLUGINS = {"uart_frames": plugin_uart_frames, "rv32i": plugin_rv32i, "runs": plugin_runs}


def gen_comb_stimulus(p, ins, rng):
    """Returns list of (compare_flag, [values])."""
    st = Stim(p, ins, rng)
    total = sum(port.width for port in ins)
    dont_care = p.get("dont_care")
    rows = []
    if total <= COMB_EXHAUSTIVE_BITS and not p.get("stimulus"):
        for code in range(1 << total):
            vals, shift = [], total
            for port in ins:
                shift -= port.width
                vals.append((code >> shift) & ((1 << port.width) - 1))
            if st.allowed(vals):
                rows.append(vals)
    else:
        n = p.get("vectors", COMB_RANDOM_VECTORS)
        rows = [st.vector() for _ in range(n)]
        if p.get("stimulus"):
            apply_plugin(p, ins, rng, rows)
    return [(0 if dont_care and check_expr(dont_care, ins, v) else 1, v) for v in rows]


def apply_plugin(p, ins, rng, rows):
    opts = p.get("stimulus_opts", {})
    over = PLUGINS[p["stimulus"]](rng, len(rows), p, opts)
    idx = {port.name: i for i, port in enumerate(ins)}
    for name, seq in over.items():
        for k, v in enumerate(seq):
            rows[k][idx[name]] = v


def gen_stateful_stimulus(p, ins, rng):
    """No clock: start from one random vector, then change one input per step."""
    st = Stim(p, ins, rng)
    n = p.get("cycles", STATEFUL_DEFAULT_STEPS)
    cur = st.vector()
    rows = [list(cur)]
    for _ in range(n - 1):
        fresh = st.vector()
        k = rng.randrange(len(ins))
        cur = list(cur)
        cur[k] = fresh[k]
        rows.append(cur)
    return [(1, v) for v in rows]


def gen_seq_stimulus(p, ins, rng):
    st = Stim(p, ins, rng)
    n = p.get("cycles", SEQ_DEFAULT_CYCLES)
    reset = p.get("reset")
    rows = [st.vector() for _ in range(n)]
    if p.get("stimulus"):
        apply_plugin(p, ins, rng, rows)
    idx = {port.name: i for i, port in enumerate(ins)}
    compare_from = 0
    init = p.get("init")
    if init:
        for k in range(init.get("cycles", 1)):
            for name, v in init["values"].items():
                rows[k][idx[name]] = v
        compare_from = init.get("cycles", 1)
    if reset:
        ri = idx[reset["name"]]
        on = 1 if str(reset.get("active", "1")) == "1" else 0
        prob = p.get("reset_prob", DEFAULT_RESET_PROB)
        for k, row in enumerate(rows):
            row[ri] = on if (k < 2 or rng.random() < prob) else 1 - on
        compare_from = max(compare_from, 2)
    return [(int(k >= compare_from), v) for k, v in enumerate(rows)]


def bits(v, w):
    return format(v, f"0{w}b")


# --------------------------------------------------------------------------
# Testbench generation
# --------------------------------------------------------------------------

TB_HEADER = """\
-- Generated by tb_check.py. Do not edit.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;
library dut, ref;

entity tb is
end entity tb;

architecture sim of tb is
  function tb_img(v : std_logic_vector) return string is
  begin
    if v'length <= 8 then
      return to_string(v);
    end if;
    return "x" & to_hstring(v);
  end function;
"""


def vhdl_value(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)


def wave_samples(mode):
    """Samples per cycle (or vector): seq logs one after each rising edge as well."""
    return 3 if mode == "seq" else 1


def gen_tb(p, ports, generics, nrows, trace, wave_pass=WAVE_PASS):
    mode = p["mode"]
    clock = p.get("clock")
    ins = [x for x in ports if x.dir == "in" and x.name != clock]
    outs = [x for x in ports if x.dir == "out"]
    per = wave_samples(mode)
    w_pass, w_before, w_after = wave_pass * per, (WAVE_BEFORE + 2) * per, WAVE_AFTER * per
    L = [TB_HEADER]
    if clock:
        L.append(f"  signal {clock} : std_logic := '0';")
    for x in ins:
        init = "'0'" if x.scalar else "(others => '0')"
        L.append(f"  signal {x.name} : {x.vtype()} := {init};")
    for x in outs:
        L.append(f"  signal {x.name}_dut, {x.name}_ref : {x.vtype()};")
    L.append("begin")
    gmap = ""
    if generics:
        gmap = " generic map (" + ", ".join(f"{k} => {vhdl_value(v)}" for k, v in generics.items()) + ")"
    for lib in ("dut", "ref"):
        assoc = []
        for x in ports:
            if x.dir == "in":
                assoc.append(f"{x.name} => {x.name}")
            else:
                assoc.append(f"{x.name} => {x.name}_{lib}")
        L.append(f"  u_{lib}: entity {lib}.top_module{gmap}")
        L.append("    port map (" + ", ".join(assoc) + ");")
    if clock:
        L.append(f"  {clock} <= not {clock} after 5 ns;")
    L.append("")
    L.append("  stim: process")
    L.append('    file tb_sf : text open read_mode is "stim.txt";')
    if trace:
        L.append('    file tb_tf : text open write_mode is "trace.txt";')
    L.append("    variable tb_sl : line;")
    L.append("    variable tb_cmp : std_logic_vector(0 downto 0);")
    L.append("    variable tb_en : boolean;")
    L.append("    variable tb_samples, tb_bad : natural := 0;")
    for x in ins:
        L.append(f"    variable tb_v_{x.name} : std_logic_vector({x.width - 1} downto 0);")
    # Waveform log (wave.txt): every sample of the first wave_pass cycles, and the samples
    # around the first mismatch, kept in a ring buffer until a mismatch shows up. A sample is
    # one vector (the inputs, then each output's reference and dut values); only the samples
    # that get written are formatted.
    fields = [x.to_slv(x.name) for x in ins]
    widths = [x.width for x in ins]
    for x in outs:
        fields += [x.to_slv(x.name + "_ref"), x.to_slv(x.name + "_dut")]
        widths += [x.width, x.width]
    L.append('    file tb_wf : text open write_mode is "wave.txt";')
    L.append("    type tb_rec_t is record")
    L.append("      ph : character; t : time; en : boolean;")
    L.append(f"      v : std_logic_vector({sum(widths) - 1} downto 0);")
    L.append("    end record;")
    L.append(f"    type tb_ring_t is array (0 to {w_before - 1}) of tb_rec_t;")
    L.append("    variable tb_ring : tb_ring_t;")
    L.append("    variable tb_idx : natural := 0;")
    L.append("    variable tb_first : integer := -1;")
    L.append("")
    L.append("    procedure tb_emit(tb_k : natural; tb_r : tb_rec_t) is")
    L.append("      variable tb_wl : line;")
    L.append("    begin")
    L.append("      write(tb_wl, tb_k); write(tb_wl, ' '); write(tb_wl, tb_r.ph); write(tb_wl, ' ');")
    L.append("      write(tb_wl, tb_r.t, right, 0, ps);")
    L.append("      if tb_r.en then write(tb_wl, string'(\" 1\")); else write(tb_wl, string'(\" 0\")); end if;")
    hi = sum(widths) - 1
    for w in widths:
        L.append(f"      write(tb_wl, ' '); write(tb_wl, to_string(tb_r.v({hi} downto {hi - w + 1})));")
        hi -= w
    L.append("      writeline(tb_wf, tb_wl);")
    L.append("    end procedure;")
    L.append("")
    L.append("    procedure tb_log(tb_ph : character; tb_en, tb_miss : boolean) is")
    L.append("      variable tb_r : tb_rec_t;")
    L.append("    begin")
    L.append(f"      if tb_first < 0 or tb_idx <= tb_first + {w_after} or tb_idx < {w_pass} then")
    L.append("        tb_r := (tb_ph, now, tb_en, " + " & ".join(fields) + ");")
    L.append("        if tb_miss and tb_first < 0 then")
    L.append("          tb_first := tb_idx;")
    L.append(f"          for tb_j in maximum(tb_idx - {w_before}, {w_pass}) to tb_idx - 1 loop")
    L.append(f"            tb_emit(tb_j, tb_ring(tb_j mod {w_before}));")
    L.append("          end loop;")
    L.append("        end if;")
    L.append(f"        if tb_idx < {w_pass} or tb_first >= 0 then")
    L.append("          tb_emit(tb_idx, tb_r);")
    L.append("        else")
    L.append(f"          tb_ring(tb_idx mod {w_before}) := tb_r;")
    L.append("        end if;")
    L.append("      end if;")
    L.append("      tb_idx := tb_idx + 1;")
    L.append("    end procedure;")
    L.append("")
    L.append("    procedure tb_check(tb_ph : character; tb_en : boolean) is")
    L.append("      variable tb_l : line;")
    L.append("      variable tb_miss : boolean := false;")
    L.append("    begin")
    for x in outs:
        L.append(f"      tb_miss := tb_miss or ({x.to_slv(x.name + '_dut')} /= {x.to_slv(x.name + '_ref')});")
    L.append("      tb_log(tb_ph, tb_en, tb_en and tb_miss);")
    if trace:
        L.append("      write(tb_l, tb_ph);")
        L.append("      if tb_en then write(tb_l, string'(\" 1\")); else write(tb_l, string'(\" 0\")); end if;")
        for x in outs:
            L.append(f"      write(tb_l, ' '); write(tb_l, to_string({x.to_slv(x.name + '_ref')}));")
        L.append("      writeline(tb_tf, tb_l);")
    L.append("      if not tb_en then return; end if;")
    L.append("      tb_samples := tb_samples + 1;")
    L.append("      if not tb_miss then return; end if;")
    L.append("      tb_bad := tb_bad + 1;")
    L.append(f"      if tb_bad > {MAX_SHOWN} then return; end if;")
    L.append("      write(tb_l, string'(\"MISMATCH|\"));")
    L.append("      write(tb_l, integer(now / 1 ns)); write(tb_l, '|'); write(tb_l, tb_ph); write(tb_l, '|');")
    for i, x in enumerate(ins):
        sep = "" if i == 0 else " "
        L.append(f"      write(tb_l, string'(\"{sep}{x.name}=\") & tb_img({x.to_slv(x.name)}));")
    for x in outs:
        d, r = x.to_slv(x.name + "_dut"), x.to_slv(x.name + "_ref")
        L.append(f"      if {d} /= {r} then")
        L.append(f"        write(tb_l, string'(\"|{x.name}|\") & tb_img({r}) & \"|\" & tb_img({d}));")
        L.append("      end if;")
    L.append("      writeline(output, tb_l);")
    L.append("    end procedure;")
    L.append("")
    L.append("    procedure tb_read_row is")
    L.append("    begin")
    L.append("      readline(tb_sf, tb_sl);")
    L.append("      read(tb_sl, tb_cmp);")
    L.append("      tb_en := tb_cmp = \"1\";")
    for x in ins:
        L.append(f"      read(tb_sl, tb_v_{x.name});")
    L.append("    end procedure;")
    L.append("")
    L.append("    procedure tb_apply is")
    L.append("    begin")
    if not ins:
        L.append("      null;")
    for x in ins:
        L.append(f"      {x.name} <= {x.from_slv('tb_v_' + x.name)};")
    L.append("    end procedure;")
    L.append("")
    L.append("    variable tb_l : line;")
    L.append("  begin")
    L.append(f"    for tb_k in 0 to {nrows - 1} loop")
    L.append("      tb_read_row;")
    if mode == "seq":
        off = float(p.get("input_offset", 0))
        L.append("      if tb_k > 0 then")
        L.append(f"        wait until falling_edge({clock});")
        L.append("        tb_check('a', tb_en);")
        L.append("      end if;")
        if off:
            L.append(f"      wait for {off} ns;")
        L.append("      tb_apply;")
        L.append("      wait for 1 ns;")
        L.append("      tb_check('b', tb_en);")
        L.append(f"      wait until rising_edge({clock});")       # for the waveform only, not graded
        L.append("      wait for 1 ns;")
        L.append("      tb_log('r', false, false);")
        L.append("    end loop;")
        L.append(f"    wait until falling_edge({clock});")
        L.append("    tb_check('a', tb_en);")
    else:
        L.append("      tb_apply;")
        L.append("      wait for 1 ns;")
        L.append("      tb_check('c', tb_en);")
        L.append("    end loop;")
    L.append("    write(tb_l, string'(\"SUMMARY|\")); write(tb_l, tb_samples); write(tb_l, '|'); write(tb_l, tb_bad);")
    L.append("    writeline(output, tb_l);")
    L.append("    std.env.finish;")
    L.append("  end process;")
    L.append("end architecture sim;")
    return "\n".join(L) + "\n"


# --------------------------------------------------------------------------
# Compile and run
# --------------------------------------------------------------------------

def ghdl_bin():
    g = os.environ.get("GHDL") or shutil.which("ghdl")
    if not g:
        raise SystemExit("ghdl not found. Put it on PATH or set GHDL=/path/to/ghdl (see README.md).")
    return g


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=RUN_TIMEOUT)


def order_sources(files):
    """Packages (*_pkg.vhd) first, keeping the given order otherwise."""
    return sorted(files, key=lambda f: 0 if f.name.endswith("_pkg.vhd") else 1)


def provided_files(p):
    pd = p["dir"] / "provided"
    if not pd.is_dir():
        return []
    order = p.get("provided_order")
    if order:
        return [pd / f for f in order]
    return order_sources(sorted(pd.glob("*.vhd")))


def learner_files(p):
    if p["mode"] == "tb":
        return [p["dir"] / "tb.vhd"]
    extra = [p["dir"] / f for f in p.get("extra_files", [])]
    top = p["dir"] / "top_module.vhd"
    return order_sources(extra) + ([top] if top not in extra else [])


def editable_files(p):
    """Learner-editable files, the one to edit first at the front."""
    files = learner_files(p)
    extra = [f for f in files if f.name != "top_module.vhd"]
    if p["mode"] != "tb" and extra and "Provided: do not edit" in (p["dir"] / "top_module.vhd").read_text():
        files = extra          # 13.6: the wrapper is given; only rev.vhd is edited
    return files


def analyze(lib, files, bdir):
    g = ghdl_bin()
    libdir = bdir / lib
    libdir.mkdir(parents=True, exist_ok=True)
    for f in files:
        r = run([g, "-a", GHDL_STD, f"--work={lib}", f"--workdir={libdir}", f"-P{libdir}", str(f)], ROOT)
        if r.returncode != 0:
            return f, (r.stdout + r.stderr).strip()
    return None, None


def verilog_hints(files):
    found = []
    for f in files:
        try:
            src = f.read_text()
        except OSError:
            continue
        code = "\n".join(line.split("--")[0] for line in src.splitlines())
        for pat, msg in VERILOG_HINTS:
            if msg not in found and re.search(pat, code):
                found.append(msg)
    return found


def grade(p, dut_files, generics_override=None, waves=True, trace=False, tag="", stimulus=None,
          wave_pass=WAVE_PASS):
    """Returns (status, detail) where status is PASS, FAIL, COMPILE, ERROR.

    stimulus replaces the generated [(compare, [input values])]; wave_pass is the length of the
    waveform of a passing run, in cycles (vectors)."""
    if p["mode"] == "tb":
        return grade_tb(p, dut_files, waves, tag)
    generics = dict(p.get("generics", {}))
    generics.update(generics_override or {})
    ports = [Port(d, generics) for d in p["ports"]]
    bdir = BUILD / (p["id"] + tag)
    if bdir.exists():
        shutil.rmtree(bdir)
    bdir.mkdir(parents=True)

    prov = provided_files(p)
    bad_file, err = analyze("dut", prov + dut_files, bdir)
    if err:
        hints = verilog_hints([f for f in dut_files if f not in prov])
        return "COMPILE", (bad_file, err, hints)
    ref_src = SOLUTIONS / f"{p['id']}.vhd"
    bad_file, err = analyze("ref", prov + [ref_src], bdir)
    if err:
        return "ERROR", f"reference failed to compile ({bad_file}):\n{err}"

    rng = random.Random(p.get("seed", 1))
    clock = p.get("clock")
    ins = [x for x in ports if x.dir == "in" and x.name != clock]
    mode = p["mode"]
    if stimulus is not None:
        rows = stimulus
    elif mode == "comb":
        rows = gen_comb_stimulus(p, ins, rng)
    elif mode == "stateful_comb":
        rows = gen_stateful_stimulus(p, ins, rng)
    elif mode == "seq":
        rows = gen_seq_stimulus(p, ins, rng)
    else:
        raise SystemExit(f"unknown mode {mode}")
    with open(bdir / "stim.txt", "w") as f:
        for cmp, vals in rows:
            f.write(" ".join([str(cmp)] + [bits(v, x.width) for v, x in zip(vals, ins)]) + "\n")
    (bdir / "tb.vhd").write_text(gen_tb(p, ports, generics, len(rows), trace, wave_pass))

    g = ghdl_bin()
    libs = [f"-P{bdir / 'dut'}", f"-P{bdir / 'ref'}"]
    r = run([g, "-a", GHDL_STD, f"--workdir={bdir}", *libs, "tb.vhd"], bdir)
    if r.returncode != 0:
        return "COMPILE", (bdir / "tb.vhd", (r.stdout + r.stderr).strip(),
                           ["The testbench could not connect to your entity. Check that the port names, "
                            "directions and types match the stub exactly."])
    cmd = [g, "--elab-run", GHDL_STD, f"--workdir={bdir}", *libs, "tb", "--ieee-asserts=disable"]
    if waves:
        cmd.append("--wave=wave.ghw")
    try:
        r = run(cmd, bdir)
    except subprocess.TimeoutExpired:
        return "ERROR", f"simulation timed out after {RUN_TIMEOUT} s (combinational loop or zero-delay oscillation?)"
    out = r.stdout + r.stderr
    (bdir / "sim.log").write_text(out)
    summary = re.search(r"^SUMMARY\|\s*(\d+)\|\s*(\d+)", out, re.M)
    if not summary:
        if "error during elaboration" in out or re.search(r"not bound|cannot be bound", out):
            return "COMPILE", (None, out.strip(), [])
        return "ERROR", "simulation stopped early:\n" + tail(out)
    samples, bad = int(summary.group(1)), int(summary.group(2))
    wave = build_wave(p, ports, bdir / "wave.txt", bad, wave_pass)
    if wave:
        (bdir / "wave.json").write_text(json.dumps(wave, separators=(",", ":")))
    mism = [line.split("|") for line in out.splitlines() if line.startswith("MISMATCH|")]
    if bad == 0:
        return "PASS", samples
    return "FAIL", (samples, bad, mism)


def read_wave_log(path, nin, nout):
    """wave.txt -> [{idx, ph, t (ns), en, ins, ref, dut}] in sample order."""
    out = {}
    if not path.is_file():
        return []
    for line in path.read_text().splitlines():
        f = line.split()
        if len(f) != 5 + nin + 2 * nout:
            continue
        vals = f[5:]
        out[int(f[0])] = {"idx": int(f[0]), "ph": f[1], "t": int(f[2]) / 1000, "en": f[4] == "1",
                          "ins": vals[:nin], "ref": vals[nin::2], "dut": vals[nin + 1::2]}
    return [out[k] for k in sorted(out)]


def build_wave(p, ports, path, bad, wave_pass=WAVE_PASS):
    """The sampled run as a waveform for the web page (None if nothing was logged).

    Samples are moved to where the change they show happened: inputs change 1 ns before the
    'b'/'c' sample, and an 'r' sample (1 ns after a rising edge) shows what the edge did.
    {t0, t1, period, clock, first, mismatches: [t], total,
     signals: [{name, dir, width, wave: [[t, bits]]} | {name, dir: "out", width, ref, dut}]}
    """
    mode, clock = p["mode"], p.get("clock")
    ins = [x for x in ports if x.dir == "in" and x.name != clock]
    outs = [x for x in ports if x.dir == "out"]
    log = read_wave_log(path, len(ins), len(outs))
    if not log:
        return None
    period = CLOCK_PERIOD if mode == "seq" else None
    step = period or 1
    for s in log:
        s["at"] = s["t"] if s["ph"] == "a" else s["t"] - 1
    miss = [s for s in log if s["en"] and s["ref"] != s["dut"]]
    first = miss[0]["t"] if bad and miss else None      # as the text report gives it
    if first is None:
        t0 = 0
        t1 = wave_pass * step
    else:
        k = int(miss[0]["at"] // step) - (1 if mode == "seq" and miss[0]["ph"] == "a" else 0)
        t0 = max(0, k - WAVE_BEFORE) * step
        t1 = (k + WAVE_AFTER) * step
    t1 = max(t1, wave_pass * step)                # the first wave_pass cycles are always logged
    t1 = min(t1, max(s["at"] for s in log) + step)
    t1 = max(t1, t0 + step)

    def track(get):
        """[[t, value]] of the changes within [t0, t1), starting with the value at t0."""
        pts = []
        for s in log:
            v, t = get(s), max(s["at"], t0)       # anything before the window collapses onto t0
            if t >= t1 or s["at"] < t0 - 2 * step:   # (the log has a gap before the ring buffer)
                continue
            if pts and pts[-1][0] == t:
                pts[-1][1] = v
                if len(pts) > 1 and pts[-2][1] == v:
                    pts.pop()
            elif not pts or pts[-1][1] != v:
                pts.append([t, v])
        return pts

    signals = []
    for i, x in enumerate(ins):
        signals.append({"name": x.name, "dir": "in", "width": x.width,
                        "wave": track(lambda s, i=i: s["ins"][i])})
    for i, x in enumerate(outs):
        signals.append({"name": x.name, "dir": "out", "width": x.width,
                        "ref": track(lambda s, i=i: s["ref"][i]), "dut": track(lambda s, i=i: s["dut"][i])})
    return {"t0": t0, "t1": t1, "period": period, "clock": clock, "first": first, "total": bad,
            "signals": signals, "mismatches": sorted({s["at"] for s in miss if t0 <= s["at"] < t1})}


# --------------------------------------------------------------------------
# Testbench-writing problems (mode "tb")
# --------------------------------------------------------------------------

def tb_variants(p):
    """[(name, files)]: the correct design first, then one entry per mutant."""
    prov = provided_files(p)
    out = [("correct", prov)]
    if p.get("tb_kind") == "mutant":
        target = p["dut_file"]
        for m in sorted((MUTANTS / p["id"]).glob("*.vhd")):
            out.append((m.stem, [m if f.name == target else f for f in prov]))
    return out


def run_tb(p, design, tb_files, rdir, waves):
    """Compile design + learner testbench into a fresh library and run entity `tb`."""
    rdir.mkdir(parents=True)
    for name in p.get("data_files", []):
        shutil.copy(p["dir"] / "provided" / name, rdir / name)
    bad_file, err = analyze("work", design + tb_files, rdir)
    if err:
        return "COMPILE", (bad_file, err, verilog_hints(tb_files))
    g = ghdl_bin()
    cmd = [g, "--elab-run", GHDL_STD, f"--workdir={rdir / 'work'}", "tb",
           "--ieee-asserts=disable", f"--stop-time={p.get('stop_time', '1ms')}"]
    if waves:
        cmd.append("--wave=wave.ghw")
    try:
        r = run(cmd, rdir)
    except subprocess.TimeoutExpired:
        return "ERROR", f"simulation timed out after {RUN_TIMEOUT} s"
    out = r.stdout + r.stderr
    (rdir / "sim.log").write_text(out)
    if r.returncode != 0 and "error during elaboration" in out:
        return "COMPILE", (None, out.strip(), [])
    errors = [l for l in out.splitlines() if re.search(r"\((assertion|report) (error|failure)\)", l)]
    if r.returncode != 0 and not errors:
        errors = [tail(out, 3) or f"simulation exited with code {r.returncode}"]
    end = re.search(r"simulation finished @(\S+)", out)
    return "RAN", {"errors": errors, "end": end.group(1) if end else None, "dir": rdir}


def read_trace(path):
    """Monitor log -> [(time, values)], keeping the last value per time step and dropping repeats."""
    last, order = {}, []
    if path.is_file():
        for line in path.read_text().splitlines():
            t, _, vals = line.strip().partition(" ")
            if t not in last:
                order.append(t)
            last[t] = vals
    out, prev = [], None
    for t in order:
        if last[t] != prev:
            out.append((int(t), last[t]))
            prev = last[t]
    return out


def to_ps(text):
    """'100ns' -> 100000; None if the simulation never called finish."""
    if not text:
        return None
    m = re.fullmatch(r"([\d.]+)(fs|ps|ns|us|ms|sec)", text)
    scale = {"fs": 1e-3, "ps": 1, "ns": 1e3, "us": 1e6, "ms": 1e9, "sec": 1e12}[m.group(2)]
    return round(float(m.group(1)) * scale)


def fmt_ps(ps):
    return f"{ps / 1000:g} ns"


def grade_tb(p, tb_files, waves, tag):
    bdir = BUILD / (p["id"] + tag)
    if bdir.exists():
        shutil.rmtree(bdir)
    bdir.mkdir(parents=True)
    variants = tb_variants(p)
    lines = []
    if p.get("tb_kind") == "trace":
        status, got = run_tb(p, variants[0][1], tb_files, bdir / "yours", waves)
        if status != "RAN":
            return status, got
        rstatus, want = run_tb(p, variants[0][1], [SOLUTIONS / f"{p['id']}.vhd"], bdir / "ref", False)
        if rstatus != "RAN":
            return "ERROR", f"reference testbench failed: {want}"
        # Changes at the very instant finish is called may or may not be logged, so drop them.
        end = to_ps(want["end"])
        exp = [e for e in read_trace(want["dir"] / "trace.txt") if end is None or e[0] < end]
        act = [a for a in read_trace(got["dir"] / "trace.txt") if end is None or a[0] < end]
        if not act:
            lines.append("The monitor logged nothing. Is it instantiated and connected?")
        for k in range(max(len(exp), len(act))):
            e = exp[k] if k < len(exp) else None
            a = act[k] if k < len(act) else None
            if e != a:
                lines.append(f"first difference at change #{k + 1}:")
                lines.append(f"  expected: " + (f"{fmt_ps(e[0]):>10}  {e[1]}" if e else "(no more changes)"))
                lines.append(f"  got:      " + (f"{fmt_ps(a[0]):>10}  {a[1]}" if a else "(no more changes)"))
                break
        if want["end"] != got["end"]:
            lines.append(f"simulation should end at {want['end']} via std.env.finish; yours "
                         + (f"ended at {got['end']}" if got["end"] else "never called finish"))
        if got["errors"]:
            lines.append("your testbench reported errors:")
            lines += ["  " + e for e in got["errors"][:5]]
        if lines:
            return "FAIL", ("tb", lines)
        return "PASS", f"{len(exp)} changes match"

    killed = 0
    for name, design in variants:
        status, res = run_tb(p, design, tb_files, bdir / name, waves and name == "correct")
        if status != "RAN":
            return status, res
        if name == "correct":
            if res["errors"]:
                lines.append("correct design: your testbench reported errors, but this design is correct:")
                lines += ["  " + e for e in res["errors"][:5]]
            else:
                lines.append("correct design: no errors reported (good)")
        elif res["errors"]:
            killed += 1
            lines.append(f"mutant {name}: killed")
        else:
            lines.append(f"mutant {name}: SURVIVED (your testbench didn't notice the bug)")
    n = len(variants) - 1
    clean = lines[0].endswith("(good)")
    if clean and killed == n:
        return "PASS", f"{n}/{n} mutants killed"
    lines.append(f"{killed}/{n} mutants killed")
    return "FAIL", ("tb", lines)


def tail(text, n=25):
    lines = [l for l in text.strip().splitlines() if not l.startswith(("MISMATCH|", "SUMMARY|"))]
    return "\n".join(lines[-n:])


def short(val, maxlen=26):
    if len(val) <= maxlen:
        return val
    return val[:11] + "…" + val[-11:]


def show_path(f):
    """A path relative to the kit, or just the file name for files outside it (the cloud grader's)."""
    f = Path(f)
    return str(f.relative_to(ROOT)) if f.is_relative_to(ROOT) else f.name


def report(p, status, detail):
    head = f"{p['section']}.{p['num']} {p['name']}"
    if status == "PASS":
        print(f"{head}: PASS ({detail}{'' if isinstance(detail, str) else ' samples'})")
        return
    if status == "COMPILE":
        f, err, hints = detail
        print(f"{head}: compile error" + (f" in {show_path(f)}" if f else ""))
        print(err)
        for h in hints:
            print(f"hint: {h}")
        return
    if status == "ERROR":
        print(f"{head}: ERROR\n{detail}")
        return
    if detail[0] == "tb":
        print(f"{head}:")
        for line in detail[1]:
            print(f"  {line}")
        print("FAIL")
        return
    samples, bad, mism = detail
    phase_name = {"a": "edge", "b": "after inputs", "c": ""}
    print(f"{head}:")
    for m in mism:
        t, ph, inputs = m[1].strip(), m[2], m[3]
        inputs = " ".join(f"{kv.split('=')[0]}={short(kv.split('=', 1)[1])}" for kv in inputs.split())
        diffs = [f"{m[i]}: expected {short(m[i + 1])}, got {short(m[i + 2])}" for i in range(4, len(m) - 2, 3)]
        when = f"{t} ns" + (f" ({phase_name[ph]})" if phase_name.get(ph) else "")
        print(f"  {when:>22} | {inputs} | " + "; ".join(diffs))
    if bad > len(mism):
        print(f"  ... {bad - len(mism)} more")
    print(f"FAIL: {bad} mismatches in {samples} samples")
    wave = BUILD / p["id"] / "wave.ghw"
    if wave.is_file():
        print(f"waveform: {show_path(wave)}")


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def cmd_list(probs):
    prog = load_progress()
    sec = None
    done = 0
    for p in probs:
        if p["section"] != sec:
            sec = p["section"]
            print(f"\nSection {sec}: {SECTION_TITLES.get(sec, '')}")
        st = prog.get(p["id"])
        mark = {"pass": "✓", "fail": "✗"}.get(st, "·")
        done += st == "pass"
        print(f"  {mark} {p['section']:>2}.{p['num']:<3} {p['name']}")
    print(f"\n{done}/{len(probs)} solved")


def selftest(probs, verbose):
    """Reference vs. itself must pass; the learner stub must compile."""
    failures = 0
    for p in probs:
        ref = SOLUTIONS / f"{p['id']}.vhd"
        status, detail = grade(p, [ref], waves=False, trace=True)
        stub_status, stub_detail = grade(p, learner_files(p), waves=False, tag=".stub")
        # An untouched stub must compile and must not already pass. Bug-hunt stubs may also
        # stop with a runtime error (16.10's range violation is the bug).
        stub_ok = ("FAIL", "ERROR") if p["section"] == 16 else ("FAIL",)
        ok = status == "PASS" and stub_status in stub_ok
        failures += not ok
        line = f"{'ok ' if ok else 'BAD'} {p['section']:>2}.{p['num']:<3} {p['name']:<24} ref:{status:<7} stub:{stub_status}"
        if ok and not verbose:
            print(line)
            continue
        print(line)
        if status != "PASS":
            report(p, status, detail)
        if stub_status not in ("PASS", "FAIL"):
            report(p, stub_status, stub_detail)
    print(f"\n{len(probs) - failures}/{len(probs)} problems ok")
    return failures == 0


def main():
    ap = argparse.ArgumentParser(description="VHDLBits grader")
    ap.add_argument("problem", nargs="*", help="problem number (3.4), name (byte_swap) or folder id")
    ap.add_argument("--list", action="store_true", help="list all problems with progress")
    ap.add_argument("-g", "--generic", action="append", default=[], metavar="NAME=VALUE",
                    help="override a top-level generic, e.g. -g W=10")
    ap.add_argument("--no-wave", action="store_true", help="skip writing build/<id>/wave.ghw")
    ap.add_argument("--selftest", action="store_true", help="maintainer check of references and stubs")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    probs = load_problems()
    if args.list:
        cmd_list(probs)
        return 0
    if args.selftest:
        sel = probs
        if args.problem:
            sel = []
            for key in args.problem:
                if re.fullmatch(r"\d+", key):
                    sel += [p for p in probs if p["section"] == int(key)]
                else:
                    p = find_problem(probs, key)
                    if not p:
                        raise SystemExit(f"no problem matches '{key}'")
                    sel.append(p)
        return 0 if selftest(sel, args.verbose) else 1
    if not args.problem:
        ap.print_help()
        return 1

    overrides = {}
    for g in args.generic:
        k, _, v = g.partition("=")
        v = v.strip()
        overrides[k.strip()] = int(v) if re.fullmatch(r"-?\d+", v) else {"true": True, "false": False}.get(v.lower(), v)
    prog = load_progress()
    rc = 0
    for key in args.problem:
        p = find_problem(probs, key)
        if not p:
            print(f"no problem matches '{key}' (try --list)")
            rc = 1
            continue
        status, detail = grade(p, learner_files(p), overrides, waves=not args.no_wave)
        report(p, status, detail)
        if status in ("PASS", "FAIL", "COMPILE") and not overrides:
            if status == "PASS" or prog.get(p["id"]) != "pass":
                prog[p["id"]] = "pass" if status == "PASS" else "fail"
            if status == "PASS":
                save_solution(p)
        rc |= status != "PASS"
    save_progress(prog)
    return rc


if __name__ == "__main__":
    sys.exit(main())
