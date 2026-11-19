import textwrap

SECTION = 15

ITER_TIMING = textwrap.indent(textwrap.dedent("""
    Timing, shared by the iterative units in this section: an edge with `start = '1'`
    while idle captures the operands. `busy` is then `'1'` for exactly {n} cycles. At the edge
    that ends the last busy cycle, the result outputs update and `done` is `'1'` for the next
    cycle only. The result outputs hold their value until the next completion. `start` is
    ignored while `busy = '1'` (it is accepted again in the `done` cycle). Active-high
    synchronous `reset` → idle, results 0, `done = '0'`.
"""), " " * 12)

PROBLEMS = [
    dict(
        num=1, name="fifo_sync", mode="seq", numeric=True,
        concept="a synchronous FIFO with first-word-fall-through.",
        intro="""
            A FIFO is a RAM plus a read pointer, a write pointer, and a count. With
            **first-word fall-through** (FWFT), the head entry is already on `dout` whenever
            the FIFO isn't empty, so `pop` acknowledges the data you're looking at rather
            than requesting new data.

            Corner cases are the whole job: simultaneous push and pop, full, empty. Decide
            each one explicitly.
        """,
        verilog="Same design; the RAM is an array signal.",
        task="""
            `generic (DEPTH : positive := 8; W : positive := 8)` (the ports are fixed at the
            defaults). At each rising edge:

            - `push = '1'` and not full: write `din` at the tail
            - `pop = '1'` and not empty: remove the head
            - both are evaluated against the state *before* the edge, so a push and a pop in
              the same cycle both happen when the FIFO is neither empty nor full; when it's
              full only the pop happens, and when it's empty only the push happens

            Outputs: `dout` shows the head entry when not empty and `x"00"` when empty;
            `empty`, `full`, and `count` (0–8) reflect the current contents. Active-high
            synchronous `reset` empties the FIFO.
        """,
        ports="clk, reset, push, pop: in sl; din: in slv(7:0); dout: out slv(7:0); full, empty: out sl; count: out slv(3:0)",
        generics={"DEPTH": 8, "W": 8},
        options={"cycles": 10000, "reset_prob": 0.002, "bias": {"push": 0.55, "pop": 0.45}},
        hints=[
            "Keep `count` as an integer `0 to DEPTH`; `empty` and `full` follow from it.",
            "Pointers wrap with `mod DEPTH`.",
        ],
    ),
    dict(
        num=2, name="uart_tx", mode="seq",
        concept="a serial transmitter: shift register plus bit counter.",
        intro="""
            The transmit side of 11.7: load a frame, shift it out one bit per clock, and tell
            the producer when you're busy.
        """,
        verilog="Same.",
        task="""
            One clock per bit. An edge with `start = '1'` while idle captures `data`; during
            the next 10 cycles `txd` carries the start bit `'0'`, the 8 data bits LSB first,
            and the stop bit `'1'`, and `busy = '1'` for all 10. Then the transmitter is idle
            again: `busy = '0'`, `txd = '1'`. `start` is ignored while `busy = '1'`. Both
            outputs are registered. Active-high synchronous `reset` → idle.
        """,
        ports="clk, reset, start: in sl; data: in slv(7:0); txd, busy: out sl",
        options={"cycles": 10000, "reset_prob": 0.001, "bias": {"start": 0.3}},
        hints=["A 10-bit shift register holding `'1' & data & '0'`, shifted right each cycle, makes `txd` its bit 0."],
    ),
    dict(
        num=3, name="uart_tx_baud", mode="seq",
        concept="a generic baud-rate divider.",
        intro="""
            Real UARTs run much slower than the clock. A counter that wraps every
            `CLKS_PER_BIT` cycles produces the bit-time tick, and the 15.2 logic only advances
            on that tick.
        """,
        verilog="`parameter CLKS_PER_BIT` becomes a generic.",
        task="""
            Same as 15.2, but each bit lasts `CLKS_PER_BIT` clock cycles, with
            `generic (CLKS_PER_BIT : positive := 4)`. `busy` is high for `10 × CLKS_PER_BIT`
            cycles. The bit timer starts at the edge that accepts `start`.
        """,
        ports="clk, reset, start: in sl; data: in slv(7:0); txd, busy: out sl",
        generics={"CLKS_PER_BIT": 4},
        options={"cycles": 10000, "reset_prob": 0.0005, "bias": {"start": 0.3}},
        hints=["A cycle counter `0 to CLKS_PER_BIT - 1`; shift and count bits when it wraps."],
    ),
    dict(
        num=4, name="spi_master", mode="seq",
        concept="generating a slower interface clock and aligning data to its edges.",
        intro="""
            SPI mode 0: the clock idles low, data changes while `sclk` is low, and both sides
            sample on the **rising** edge of `sclk`. Inside an FPGA, `sclk` is just a
            registered output toggled by a counter; it is never used as a clock.
        """,
        verilog="Same.",
        task="""
            `sclk` runs at clk/4. While idle: `cs_n = '1'`, `sclk = '0'`, `mosi = '0'`,
            `done = '0'`.

            An edge with `start = '1'` while idle captures `tx`, sets `cs_n = '0'` and puts
            `tx(7)` on `mosi`. The transfer then lasts 32 cycles, numbered `c = 0 … 31` from
            the cycle after that edge:

            ```
            c        : 0  1  2  3  4  5  6  7  ...  28 29 30 31 | idle
            sclk     : 0  0  1  1  0  0  1  1  ...   0  0  1  1 |  0
            mosi     : b7 b7 b7 b7 b6 b6 b6 b6 ...  b0 b0 b0 b0 |  0
            cs_n     : 0  0  0  0  0  0  0  0  ...   0  0  0  0 |  1
            done     : 0  0  0  0  0  0  0  0  ...   0  0  0  0 |  1 (one cycle)
            ```

            - `miso` is sampled at the clock edge that ends cycle `c = 4k + 1` (where `sclk`
              rises), MSB first.
            - At the edge that ends cycle 31, `cs_n` returns to `'1'`, `done` is `'1'` for
              one cycle, and `rx` takes the received byte (it holds until the next
              completion).

            `start` is ignored while `cs_n = '0'`. All outputs are registered. Active-high
            synchronous `reset` → idle, `rx = x"00"`.
        """,
        ports="clk, reset, start, miso: in sl; tx: in slv(7:0); sclk, mosi, cs_n, done: out sl; rx: out slv(7:0)",
        options={"cycles": 10000, "reset_prob": 0.0005, "bias": {"start": 0.3}},
        hints=[
            "One counter `0 to 31` gives everything: `sclk` is bit 1 of the next count.",
            "Shift `tx` left when `sclk` falls; shift `miso` in when it rises.",
        ],
    ),
    dict(
        num=5, name="debounce_edge", mode="seq",
        concept="composing two earlier designs.",
        intro="""
            Real designs are mostly compositions of small, well-tested pieces. This one is
            11.6 (with a longer window) followed by 8.5.
        """,
        verilog="Same.",
        task="""
            Debounce `btn` like 11.6, but `clean` only changes at the **8th** consecutive edge
            where `btn` differs from it. Output `press = '1'` for exactly one cycle each time
            `clean` goes from `'0'` to `'1'`: `press` rises at the same edge as `clean`.
            `clean` itself is internal. Active-high synchronous `reset` → `clean = '0'`,
            `press = '0'`, counter restarted.
        """,
        ports="clk, reset, btn: in sl; press: out sl",
        options={"cycles": 10000, "reset_prob": 0.0005, "stimulus": "runs", "stimulus_opts": {"port": "btn", "min": 1, "max": 20}},
        after_ports="The grader drives `btn` with bouncy runs of 1–20 cycles.",
        hints=["`press` is set at the same edge that flips `clean` to `'1'`, and cleared at every other edge."],
    ),
    dict(
        num=6, name="seven_seg_mux", mode="seq", numeric=True,
        concept="time-multiplexed display (like the Nexys A7's 8-digit display).",
        intro="""
            Multi-digit 7-segment displays share the segment lines between digits. The design
            enables one digit at a time (active-low anodes) and shows that digit's pattern,
            cycling fast enough that the eye sees all digits lit at once.
        """,
        verilog="Same.",
        task="""
            Show the 16-bit `value` on 4 digits. Digit `k` shows `value(4k+3 downto 4k)` using
            the 7.5 encoding (active-low, `seg(6 downto 0) = g f e d c b a`). A digit counter
            `k` advances every 4 clocks (0, 1, 2, 3, 0, …). `an(k) = '0'` for the active
            digit and `'1'` for the others.

            `an` and `seg` are combinational from `k` and the current `value`. Active-high
            synchronous `reset` → digit 0 at the start of its 4-cycle slot.
        """,
        ports="clk, reset: in sl; value: in slv(15:0); an: out slv(3:0); seg: out slv(6:0)",
        options={"cycles": 10000, "reset_prob": 0.002},
        hints=["Reuse your 7.5 glyph table; the digit counter is the top two bits of a 4-bit counter."],
    ),
    dict(
        num=7, name="moving_avg4", mode="seq", numeric=True,
        concept="a DSP-style sliding window.",
        intro="""
            A moving average keeps the last N samples in a shift register. With N a power of
            two, the division is a shift. Mind the width of the sum: four 8-bit values need 10
            bits.
        """,
        verilog="Same.",
        task="""
            Keep the last 4 accepted samples. At each edge with `valid = '1'`, shift `x` into
            the history. `y` is `(sum of the 4 history samples) / 4` rounded down, computed
            combinationally from the history (so it changes after the edge that accepts a
            sample). Active-high synchronous `reset` clears the history to 0.
        """,
        ports="clk, reset, valid: in sl; x: in slv(7:0); y: out slv(7:0)",
        options={"cycles": 10000, "reset_prob": 0.002, "bias": {"valid": 0.7}},
        hints=["A 10-bit sum, then `y <= sum(9 downto 2)`."],
    ),
    dict(
        num=8, name="fir4", mode="seq", numeric=True,
        concept="a constant-coefficient FIR filter.",
        intro="""
            A finite impulse response filter is a weighted sum of the last few samples. With
            small constant coefficients, synthesis turns the multiplications into shifts and
            adds (`3·x = 2x + x`).
        """,
        verilog="Same; watch the signed widths.",
        task="""
            4-tap FIR with coefficients `(1, 3, 3, 1)` on 8-bit signed samples. Keep a delay
            line `d0, d1, d2` of the previous accepted samples (`d0` newest). At each edge
            with `valid = '1'`:

            - `y ← x + 3·d0 + 3·d1 + d2` (11-bit signed; it can't overflow)
            - the delay line shifts: `d2 ← d1`, `d1 ← d0`, `d0 ← x`

            When `valid = '0'` nothing changes. `y` is registered. Active-high synchronous
            `reset` clears the delay line and `y` to 0.
        """,
        ports="clk, reset, valid: in sl; x: in slv(7:0); y: out slv(10:0)",
        options={"cycles": 10000, "reset_prob": 0.002, "bias": {"valid": 0.7}},
        hints=["`resize` every term to 11 bits before adding; `3 * d` on an 11-bit `signed` gives 22 bits, so `resize` the product too (or write `d + d + d`)."],
    ),
    dict(
        num=9, name="isqrt_seq", mode="seq", numeric=True,
        concept="an iterative datapath with a start/busy/done handshake.",
        intro="""
            Some functions are too big to compute in one cycle, so you compute one bit per
            cycle and handshake with the user. Bit-by-bit square root: for each result bit,
            from the top, tentatively set it and keep it if the square still fits.
        """ + ITER_TIMING.format(n=8),
        verilog="Same.",
        task="`root = floor(sqrt(x))` for the 16-bit unsigned `x` captured at start, computed over 8 busy cycles (one result bit per cycle).",
        ports="clk, reset, start: in sl; x: in slv(15:0); root: out slv(7:0); busy, done: out sl",
        options={"cycles": 10000, "reset_prob": 0.0005, "bias": {"start": 0.3}},
        hints=[
            "Keep a partial root `r`. In the step for bit `b`: `t := r or (bit b)`; if `t * t <= x` then `r := t`.",
            "`t * t` on an 8-bit `unsigned` is 16 bits, the same width as `x`.",
        ],
    ),
    dict(
        num=10, name="mult_seq", mode="seq", numeric=True,
        concept="shift-and-add multiplication.",
        intro="""
            The hardware version of long multiplication: for each bit of the multiplier, add
            the shifted multiplicand to an accumulator if the bit is 1.
        """ + ITER_TIMING.format(n=8),
        verilog="Same.",
        task="`p = a × b` (8×8 unsigned → 16 bits) for the operands captured at start, computed over 8 busy cycles.",
        ports="clk, reset, start: in sl; a, b: in slv(7:0); p: out slv(15:0); busy, done: out sl",
        options={"cycles": 10000, "reset_prob": 0.0005, "bias": {"start": 0.3}},
        hints=["Shift the multiplier right and the multiplicand left each cycle."],
    ),
    dict(
        num=11, name="div_seq", mode="seq", numeric=True,
        concept="restoring division.",
        intro="""
            Restoring division brings down one dividend bit per cycle into a partial
            remainder, subtracts the divisor if it fits, and records a quotient bit.
        """ + ITER_TIMING.format(n=16),
        verilog="Same.",
        task="""
            Divide the 16-bit unsigned `n` by the 8-bit unsigned `d` (captured at start) over
            16 busy cycles: `q = n / d`, `r = n mod d`, `dz = '0'`.

            Dividing by zero takes the same 16 cycles and gives `q = x"FFFF"`,
            `r = n(7 downto 0)` and `dz = '1'`. `dz` updates and holds together with `q` and `r`.
        """,
        ports="clk, reset, start: in sl; n: in slv(15:0); d: in slv(7:0); q: out slv(15:0); r: out slv(7:0); busy, done, dz: out sl",
        options={"cycles": 10000, "reset_prob": 0.0005, "bias": {"start": 0.3}, "value_bias": {"d": [[0, 0.1]]}},
        hints=["The partial remainder needs 9 bits: shift in one dividend bit, compare against `d`, subtract if it fits."],
    ),
    dict(
        num=12, name="rv32i_alu", numeric=True,
        concept="a real ALU, bridge to the RISC-V core.",
        intro="""
            The RV32I integer ALU is selected by the instruction's `funct3` plus bit 5 of
            `funct7` (which distinguishes ADD/SUB and SRL/SRA). Shift amounts use only the low
            5 bits of `b`.
        """,
        verilog="Same; arithmetic shift right is `shift_right` on `signed`.",
        task="""
            | `funct7_5` | `funct3` | operation |
            |---|---|---|
            | 0 | `000` | ADD: `a + b` |
            | 1 | `000` | SUB: `a - b` |
            | x | `001` | SLL: `a << b(4:0)` |
            | x | `010` | SLT: 1 if `a < b` signed, else 0 |
            | x | `011` | SLTU: 1 if `a < b` unsigned, else 0 |
            | x | `100` | XOR |
            | 0 | `101` | SRL: logical `a >> b(4:0)` |
            | 1 | `101` | SRA: arithmetic `a >> b(4:0)` |
            | x | `110` | OR |
            | x | `111` | AND |

            All results are 32 bits and wrap.
        """,
        ports="a, b: in slv(31:0); funct3: in slv(2:0); funct7_5: in sl; y: out slv(31:0)",
        options={"vectors": 3000, "copy": [["b", "a", 0.05]]},
        hints=["A `case funct3 is` with `funct7_5` tested inside the `000` and `101` branches."],
    ),
    dict(
        num=13, name="rv32i_imm_gen",
        concept="immediate formats: the bit-scrambling that makes RISC-V decoders small.",
        intro="""
            RISC-V keeps the sign bit of every immediate at `instr(31)` and reuses bit
            positions across formats, so the immediate generator is just muxed slices. The
            B and J formats encode multiples of 2, so bit 0 is always 0.
        """,
        verilog="Same slices and concatenations.",
        task="""
            Generate the 32-bit sign-extended immediate from `instr`, choosing the format from
            the opcode `instr(6 downto 0)`:

            | opcode | format | immediate |
            |---|---|---|
            | `0000011` (load), `0010011` (op-imm), `1100111` (jalr) | I | `instr[31:20]` |
            | `0100011` (store) | S | `instr[31:25] & instr[11:7]` |
            | `1100011` (branch) | B | `instr[31] & instr[7] & instr[30:25] & instr[11:8] & '0'` |
            | `0110111` (lui), `0010111` (auipc) | U | `instr[31:12] & x"000"` |
            | `1101111` (jal) | J | `instr[31] & instr[19:12] & instr[20] & instr[30:21] & '0'` |
            | anything else | — | 0 |

            I, S, B and J immediates are sign-extended from their top bit (always `instr(31)`).
        """,
        ports="instr: in slv(31:0); imm: out slv(31:0)",
        options={"stimulus": "rv32i", "stimulus_opts": {"port": "instr"}, "vectors": 3000},
        after_ports="The grader biases `instr` toward valid RV32I opcodes.",
        hints=["A `case` on the opcode; each branch is one concatenation with `(n downto 0 => instr(31))` for the sign extension."],
    ),
    dict(
        num=14, name="rv32i_decoder",
        concept="the main control decoder of a single-cycle CPU.",
        intro="""
            The control decoder turns an opcode into the datapath's control signals. A table
            is the specification; a `case` on the opcode with default assignments is the
            implementation.
        """,
        verilog="Same.",
        task="""
            Decode `instr` (opcode = `instr(6 downto 0)`, `funct3 = instr(14 downto 12)`,
            `funct7_5 = instr(30)`):

            | opcode | reg_write | alu_src | mem_read | mem_write | mem_to_reg | branch | jump | alu_ctrl |
            |---|---|---|---|---|---|---|---|---|
            | `0110011` R-type | 1 | 0 | 0 | 0 | 0 | 0 | 0 | `funct7_5 & funct3` |
            | `0010011` op-imm | 1 | 1 | 0 | 0 | 0 | 0 | 0 | `funct7_5 & funct3` if `funct3 = 101`, else `'0' & funct3` |
            | `0000011` load | 1 | 1 | 1 | 0 | 1 | 0 | 0 | `0000` |
            | `0100011` store | 0 | 1 | 0 | 1 | 0 | 0 | 0 | `0000` |
            | `1100011` branch | 0 | 0 | 0 | 0 | 0 | 1 | 0 | `1000` |
            | `1101111` jal | 1 | 0 | 0 | 0 | 0 | 0 | 1 | `0000` |
            | `1100111` jalr | 1 | 1 | 0 | 0 | 0 | 0 | 1 | `0000` |
            | `0110111` lui | 1 | 1 | 0 | 0 | 0 | 0 | 0 | `0000` |
            | `0010111` auipc | 1 | 1 | 0 | 0 | 0 | 0 | 0 | `0000` |
            | anything else | 0 | 0 | 0 | 0 | 0 | 0 | 0 | `0000` |

            `alu_ctrl` uses the 15.12 encoding (`funct7_5 & funct3`).
        """,
        ports="instr: in slv(31:0); reg_write, alu_src, mem_read, mem_write, mem_to_reg, branch, jump: out sl; alu_ctrl: out slv(3:0)",
        options={"stimulus": "rv32i", "stimulus_opts": {"port": "instr"}, "vectors": 3000},
        after_ports="The grader biases `instr` toward valid RV32I opcodes.",
        hints=["Default every output to `'0'`/`\"0000\"`, then a `case` on the opcode."],
    ),
]
