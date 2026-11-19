SECTION = 10

PROBLEMS = [
    dict(
        num=1, name="shift4", mode="seq",
        concept="shifting via slice-and-concatenate.",
        intro="""
            A shift register is a register whose next value is a slice of itself plus a new
            bit:

            ```vhdl
            hist <= hist(6 downto 0) & sample;     -- shift left, new bit enters at the bottom
            ```

            Priorities between controls are just the order of the `if`/`elsif` chain.
        """,
        verilog="`q <= {1'b0, q[3:1]};` becomes `q <= '0' & q(3 downto 1);`.",
        task="""
            4-bit shift register `q` with:

            - asynchronous active-high reset `areset` → `"0000"`
            - `load = '1'`: load `d` (highest priority after reset)
            - else `en = '1'`: shift right by one; the MSB fills with `'0'`
            - otherwise hold
        """,
        ports="clk, areset, load, en: in sl; d: in slv(3:0); q: out slv(3:0)",
        options={"bias": {"load": 0.15}},
        hints=["`if areset = '1' then ... elsif rising_edge(clk) then if load ... elsif en ...`"],
    ),
    dict(
        num=2, name="rotate8", mode="seq", numeric=True,
        concept="`rotate_left`/`rotate_right` from `numeric_std`, or by hand.",
        intro="""
            A rotation moves the bit that falls off one end back in at the other.
            `numeric_std` provides `rotate_left(x, n)` and `rotate_right(x, n)` for
            `unsigned` and `signed`; with slices it's `v(0) & v(7 downto 1)` (right by one).
        """,
        verilog="`{q[0], q[7:1]}`.",
        task="""
            8-bit register `q`, no reset. On an edge with `load = '1'`, load `d`. Otherwise
            `ena = "01"` rotates right by one, `"10"` rotates left by one, and `"00"`/`"11"`
            hold.
        """,
        ports="clk, load: in sl; ena: in slv(1:0); d: in slv(7:0); q: out slv(7:0)",
        options={"bias": {"load": 0.1}, "init": {"values": {"load": 1}}},
        after_ports="With no reset, the grader asserts `load` in the first cycle so the register starts from a known value.",
        hints=["A `case ena is` inside `elsif` of the load test."],
    ),
    dict(
        num=3, name="arith_shift", mode="seq", numeric=True,
        concept="`shift_right` on `signed` replicates the sign bit.",
        intro="""
            `shift_right(signed(x), n)` fills from the left with copies of the sign bit, which
            divides by 2ⁿ rounding toward −∞. On `unsigned` it fills with zeros.
        """,
        verilog="`>>>` on a `signed` reg is `shift_right` on `signed`.",
        task="""
            16-bit register `q`, no reset. On an edge with `load = '1'`, load `d`. Otherwise,
            when `en = '1'`, `amt` selects:

            | `amt` | operation |
            |---|---|
            | `00` | shift left by 1 |
            | `01` | shift left by 4 |
            | `10` | arithmetic shift right by 1 |
            | `11` | arithmetic shift right by 4 |
        """,
        ports="clk, load, en: in sl; amt: in slv(1:0); d: in slv(15:0); q: out slv(15:0)",
        options={"bias": {"load": 0.1}, "init": {"values": {"load": 1}}},
        after_ports="With no reset, the grader asserts `load` in the first cycle so the register starts from a known value.",
        hints=["Keep the register as `signed`; `shift_left` and `shift_right` both work on it."],
    ),
    dict(
        num=4, name="lfsr5", mode="seq",
        concept="Galois LFSR.",
        intro="""
            A **linear feedback shift register** produces a pseudo-random sequence. In the
            **Galois** form, the register shifts one way and the bit falling off the end is
            XORed into a few fixed *tap* positions as it wraps around. With the right taps it
            visits every non-zero state before repeating (2ⁿ − 1 states). The all-zero state
            is a trap, so never reset to zero.

            Tap positions are traditionally numbered from 1. A tap at position `n` (the
            register width) is just the wrap-around itself.
        """,
        verilog="Same structure: a concatenation with a few XORs.",
        task="""
            5-bit Galois LFSR with taps at positions 5 and 3 (period 31). At each edge the
            register shifts **right**:

            - `q(4)` gets the old `q(0)` (the wrap-around, tap 5)
            - `q(2)` gets the old `q(3) XOR q(0)` (tap 3)
            - every other bit gets its left neighbour: `q(3) ← q(4)`, `q(1) ← q(2)`, `q(0) ← q(1)`

            Active-high synchronous `reset` to `"00001"`.
        """,
        ports="clk, reset: in sl; q: out slv(4:0)",
        hints=["One concatenation: `q(0) & q(4) & (q(3) xor q(0)) & q(2) & q(1)`."],
    ),
    dict(
        num=5, name="sipo8", mode="seq",
        concept="serial-to-parallel with a bit counter.",
        intro="""
            Serial-in, parallel-out: shift bits in one at a time and count them. When a full
            word has arrived, publish it and raise a one-cycle strobe. For **LSB-first**
            data, shift right and enter new bits at the top, so the first bit ends up in
            bit 0.
        """,
        verilog="Same structure.",
        task="""
            On each edge with `en = '1'`, accept the bit on `sin` into a shift register
            (LSB first). On the edge that accepts the 8th bit of a byte, copy the complete
            byte to `dout` and set `valid` to `'1'`; `valid` is `'0'` after every other edge.
            `dout` holds its value until the next byte completes.

            Active-high synchronous `reset` clears the bit count, `dout` and `valid` to 0.
        """,
        ports="clk, reset, en, sin: in sl; dout: out slv(7:0); valid: out sl",
        options={"bias": {"en": 0.8}, "reset_prob": 0.01},
        hints=[
            "A bit counter 0–7. On the 8th accepted bit the counter is 7, and the byte is `sin & sr(7 downto 1)`.",
        ],
    ),
    dict(
        num=6, name="piso8", mode="seq",
        concept="parallel-in serial-out with busy.",
        intro="""
            Parallel-in, serial-out: capture a word, then shift it out one bit per cycle while
            flagging `busy`. A `busy` output lets the producer know when it may load again.
        """,
        verilog="Same structure.",
        task="""
            While idle (`busy = '0'`), an edge with `load = '1'` captures `d`. During the next
            8 cycles `busy = '1'` and `sout` shows `d(7)`, `d(6)`, …, `d(0)`, one bit per
            cycle, MSB first. After those 8 cycles `busy` returns to `'0'` and `sout` to
            `'0'`. `load` is ignored on edges where `busy = '1'`.

            Active-high synchronous `reset` → idle, `sout = '0'`. Both outputs are registered.
        """,
        ports="clk, reset, load: in sl; d: in slv(7:0); sout, busy: out sl",
        options={"bias": {"load": 0.3}, "reset_prob": 0.01},
        hints=[
            "Keep a bits-remaining counter alongside the shift register.",
            "On the load edge, `sout <= d(7)` and the register keeps the remaining 7 bits.",
        ],
    ),
    dict(
        num=7, name="shift_n_generic", mode="seq",
        concept="a generic-width shift register with serial in and out.",
        intro="""
            With a generic width, write slices in terms of the generic:
            `q(N - 2 downto 0) & sin`.
        """,
        verilog="`parameter N` becomes a generic.",
        task="""
            `generic (N: positive := 12)`. On each edge with `en = '1'`, shift `q` left by one
            with `sin` entering at bit 0. `sout` is the MSB `q(N-1)`. No reset.
        """,
        ports="clk, en, sin: in sl; sout: out sl; q: out slv(N-1:0)",
        generics={"N": 12},
        hints=["Use an internal signal for the register so you can read it, or read the `out` port in VHDL-2008."],
    ),
    dict(
        num=8, name="lfsr32", mode="seq",
        concept="a wide Galois LFSR.",
        intro="""
            Same structure as 10.4, wider. Taps at 32, 22, 2, 1 give a maximal-length
            sequence of 2³² − 1 states.
        """,
        verilog="Same structure.",
        task="""
            32-bit Galois LFSR with taps at positions 32, 22, 2, 1. At each edge the register
            shifts **right**, and the old `q(0)` is XORed in at each tap:

            - `q(31)` gets the old `q(0)`
            - `q(21)` gets `q(22) XOR q(0)`
            - `q(1)` gets `q(2) XOR q(0)`
            - `q(0)` gets `q(1) XOR q(0)`
            - every other bit `q(i)` gets `q(i+1)`

            Active-high synchronous `reset` to `x"00000001"`.
        """,
        ports="clk, reset: in sl; q: out slv(31:0)",
        hints=["Shift first (`'0' & q(31 downto 1)`), then XOR a mask built from `q(0)`."],
    ),
    dict(
        num=9, name="tap_lut", mode="seq", numeric=True,
        concept="a shift register plus a read mux behaves like a LUT (this is how SRL primitives work).",
        intro="""
            Xilinx FPGAs can configure a LUT as a 16- or 32-bit shift register with an
            addressable output (SRL16/SRL32). Describe exactly that and synthesis maps it to
            one LUT instead of a chain of flip-flops: a shift register with no reset plus a
            mux.
        """,
        verilog="Same.",
        task="""
            An 8-bit shift register `sr` shifts left on each edge with `en = '1'`, with `sin`
            entering at bit 0. The output `y = sr(addr)`, read combinationally. No reset.
        """,
        ports="clk, en, sin: in sl; addr: in slv(2:0); y: out sl",
        hints=["`y <= sr(to_integer(unsigned(addr)));`"],
    ),
    dict(
        num=10, name="rule90", mode="seq",
        concept="a 1-D cellular automaton; every cell updates in parallel.",
        intro="""
            A cellular automaton updates every cell at once from its neighbours. Because a
            clocked process computes *all* next values from the *old* register, parallel
            update comes for free. Out-of-range neighbours are handled with padding:

            ```vhdl
            padded := '0' & cells & '0';     -- now padded(i+2) and padded(i) are the neighbours of cells(i)
            ```
        """,
        verilog="Same as an XOR of two shifted copies.",
        task="""
            64 cells in `q`. On an edge with `load = '1'`, load `d`. Otherwise each cell
            becomes `left XOR right`, where `left` is `q(i+1)` and `right` is `q(i-1)`; cells
            beyond either end count as `'0'`. No reset.
        """,
        ports="clk, load: in sl; d: in slv(63:0); q: out slv(63:0)",
        options={"bias": {"load": 0.03}, "init": {"values": {"load": 1}}},
        hints=["The whole update is one line: XOR of `q` shifted left by one and `q` shifted right by one."],
    ),
    dict(
        num=11, name="rule30", mode="seq",
        concept="a different neighbourhood rule.",
        intro="""
            Rule 30 looks simple but produces chaotic patterns. Mathematica used it as a
            random number generator.
        """,
        verilog="Same idea.",
        task="""
            Same as `rule90`, but the next state of cell `i` is `left XOR (center OR right)`,
            with `left = q(i+1)`, `center = q(i)`, `right = q(i-1)`, and `'0'` beyond the ends.
        """,
        ports="clk, load: in sl; d: in slv(63:0); q: out slv(63:0)",
        options={"bias": {"load": 0.03}, "init": {"values": {"load": 1}}},
        hints=["Build `left` and `right` vectors by shifting `q` with zero fill."],
    ),
    dict(
        num=12, name="life16", mode="seq", numeric=True,
        concept="2-D indexing on a flattened vector; generate loops over two dimensions.",
        intro="""
            A 2-D grid flattened into a vector is indexed as `row * WIDTH + col`. With
            wraparound (a torus), neighbour coordinates are taken `mod` the grid size.

            Nested `for` loops in a clocked process (or nested `for ... generate`) visit every
            cell. Count each cell's live neighbours with a variable, then apply the rule.
        """,
        verilog="Same indexing; `%` is `mod`.",
        task="""
            Conway's Game of Life on a 16×16 torus (edges wrap in both directions). Cell
            `(r, c)` is bit `r*16 + c` of `q`. On an edge with `load = '1'`, load `d`;
            otherwise advance one generation:

            - a live cell with 2 or 3 live neighbours stays alive, otherwise it dies
            - a dead cell with exactly 3 live neighbours becomes alive

            Each cell has 8 neighbours. No reset.
        """,
        ports="clk, load: in sl; d: in slv(255:0); q: out slv(255:0)",
        options={"bias": {"load": 0.02, "d": 0.3}, "init": {"values": {"load": 1}}},
        hints=[
            "A helper function `cell(r, c)` that returns `q(((r mod 16) * 16) + (c mod 16))` keeps the loop readable. Pass `r + 15` instead of `r - 1` so the argument stays natural.",
        ],
    ),
]
