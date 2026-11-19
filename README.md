# VHDLBits

220 small VHDL-2008 problems for people who already know Verilog, from one-line
assignments up to FSMs, testbenches, and a few bigger builds. Each problem introduces one
idea. Your design is checked automatically by simulating it against a reference design.

**Try it at <https://vhdl.drewngo.com>.** No account needed; your code and progress are
kept in your browser.

This repository is the source for that site. It isn't set up as a kit to install, but
everything is here: the problems, the grader, the reference answers, and the site itself.

Inspired by [HDLBits](https://hdlbits.01xz.net) by Henry Wong. Not affiliated.

## How grading works

The grader compiles your design into a library called `dut` and the reference answer into
a library called `ref`; both use entity `top_module`. A generated testbench drives both
with identical stimulus and compares every output, exactly (`'Z'`, `'U'` and `'X'` must
match too).

- **Combinational problems:** every input combination if there are 12 input bits or
  fewer, otherwise 1000 random vectors with a fixed seed. Outputs are compared 1 ns after
  each vector.
- **Sequential problems:** a 10 ns clock for about 300 cycles (more for the bigger ones).
  Inputs change on the falling edge, and outputs are compared twice per cycle: at the
  falling edge, before new inputs (the registered state), and 1 ns after the new inputs (catches
  Mealy outputs and async vs. sync reset). Reset is held for the first 2 cycles and then
  asserted at random; comparison starts once the first reset is over. Without a reset,
  comparison starts at cycle 0, and `'U'` on both sides counts as a match.
- **Latch problems** have no clock: one input changes at a time and outputs are compared
  after each change.
- **Testbench problems (Section 14):** either your testbench's signals are logged by a
  provided `monitor` and compared against the reference testbench's log, or your
  testbench is run against the correct design (it must report no errors) and against
  several buggy *mutants* (it must report an error for each).

A failure prints the first 10 mismatches as `time | inputs | output: expected X, got Y`
and a summary such as `FAIL: 37 mismatches in 600 samples`. Compile errors are shown as GHDL
reports them, with a one-line hint when a Verilog habit shows up (`1'b1`, `assign`,
`always`, `==`, …).

On the web page every check also draws a waveform of the run: your outputs next to the
reference's, with the differences shaded. A pass shows the first 24 cycles (or input
vectors); a failure shows the cycles around the first mismatch. The testbench keeps the
recent samples in a ring buffer and writes only that window, so it costs almost nothing.

## Sections

| # | Section | Problems |
|---|---|---|
| 1 | Getting Started | 3 |
| 2 | Language Basics | 15 |
| 3 | Vectors | 18 |
| 4 | Hierarchy | 15 |
| 5 | Processes | 14 |
| 6 | Types & `numeric_std` | 17 |
| 7 | Combinational Circuits | 21 |
| 8 | Sequential Basics | 15 |
| 9 | Counters | 14 |
| 10 | Shift Registers & Automata | 12 |
| 11 | Finite State Machines | 25 |
| 12 | Memories | 8 |
| 13 | Packages, Records & Types | 7 |
| 14 | Writing Testbenches | 8 |
| 15 | Bigger Builds | 14 |
| 16 | Bug Hunts | 14 |

## What's here

| path | what it is |
|---|---|
| `problems/` | one folder per problem: the statement (`README.md`), diagram, starter code and grader settings |
| `solutions/` | the reference answers (spoilers), which the grader compares you against |
| `check.py` | the grader: builds a testbench around your design and the reference, with GHDL |
| `frontend/` | the problem page |
| `tools/` | generators for the problems and diagrams, and independent Python models that check every reference answer |
| `grader/` | the online grader (Cloud Run) and the Cloudflare Worker in front of it |
