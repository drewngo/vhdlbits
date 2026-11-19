SECTION = 7

# Hidden functions for the waveform puzzles. Only the tables below reach the READMEs.
_PUZZLE1 = lambda a, b, c: (a & (1 - b)) | (b & c)
_PUZZLE2 = lambda a, b, c, d: a ^ (b & (c | d))
PUZZLE_VEC = [0x7, 0xC, 0x2, 0x9, 0xE, 0x0, 0x5, 0xB, 0x3, 0xF, 0x8, 0x1, 0xA, 0x6, 0xD, 0x4]

# A fixed, scrambled visiting order makes the tables read like a simulation trace
# rather than a sorted truth table.
_ORDER8 = [5, 0, 3, 6, 1, 7, 2, 4]
_ORDER16 = [9, 2, 14, 0, 7, 11, 4, 13, 1, 8, 15, 6, 3, 10, 12, 5]


def _trace(names, order, width, fn):
    head = "| time | " + " | ".join(names) + " |\n|---|" + "---|" * len(names) + "\n"
    rows = []
    for k, v in enumerate(order):
        ins = [(v >> (width - 1 - j)) & 1 for j in range(width)]
        rows.append(f"| {10 * k} ns | " + " | ".join(map(str, ins + [fn(*ins)])) + " |")
    return head + "\n".join(rows)


def _trace_vec():
    head = "| time | x | q |\n|---|---|---|\n"
    rows = [f"| {10 * k} ns | `{v:04b}` | `{PUZZLE_VEC[v]:04b}` |" for k, v in enumerate(_ORDER16)]
    return head + "\n".join(rows)


PUZZLE1_TABLE = _trace(["a", "b", "c", "q"], _ORDER8, 3, _PUZZLE1)
PUZZLE2_TABLE = _trace(["a", "b", "c", "d", "q"], _ORDER16, 4, _PUZZLE2)
PUZZLE_VEC_TABLE = _trace_vec()

PROBLEMS = [
    dict(
        num=1, name="half_adder",
        concept="the smallest arithmetic circuit.",
        intro="""
            A half adder adds two bits. The sum bit is the XOR, and the carry is the AND.
            Every bigger adder is built from this idea.
        """,
        verilog="`assign {c, s} = a + b;` works in Verilog because the target width grows the add. In VHDL, write the gates or use `numeric_std` with explicit widths.",
        task="Add `a` and `b`: `s` is the sum bit, `c` the carry.",
        ports="a, b: in sl; s, c: out sl",
        hints=["Two gates."],
    ),
    dict(
        num=2, name="full_adder",
        concept="adding a carry-in.",
        intro="""
            A full adder adds three bits. The sum is the XOR of all three; the carry-out is
            `'1'` when at least two inputs are `'1'` (the majority function from 2.12).
        """,
        verilog="Same gates; remember the parentheses around each product term.",
        task="Add `a`, `b` and `cin`: `s` is the sum bit, `cout` the carry-out.",
        ports="a, b, cin: in sl; s, cout: out sl",
        hints=["`cout` is the majority of the three inputs."],
    ),
    dict(
        num=3, name="adder4_loop",
        concept="ripple carry written as a `for` loop with a variable, no instances.",
        intro="""
            A loop with a carry variable describes a ripple-carry chain without any
            sub-modules. Each iteration reads the carry from the previous one:

            ```vhdl
            process(all)
              variable c : std_logic;
            begin
              c := '0';
              for i in 0 to 7 loop
                res(i) <= p(i) xor c;
                c := p(i) and c;           -- an incrementer's carry chain
              end loop;
            end process;
            ```
        """,
        verilog="Same as a `for` loop with a blocking carry variable.",
        task="4-bit adder: `sum = a + b + cin` with carry-out `cout`. Write it as a loop with a carry variable, not with `numeric_std` `+`.",
        ports="a, b: in slv(3:0); cin: in sl; sum: out slv(3:0); cout: out sl",
        hints=["The loop body is the 7.2 full adder; `cout` gets the carry variable after the loop."],
    ),
    dict(
        num=4, name="decoder3to8",
        concept="one-hot output with enable.",
        intro="""
            A decoder turns a binary index into a one-hot vector. With `numeric_std`, you can
            set one bit at an integer position:

            ```vhdl
            process(all)
            begin
              sel_lines <= (others => '0');
              sel_lines(to_integer(unsigned(idx))) <= '1';
            end process;
            ```

            Assigning an element after the whole vector is fine: last assignment wins per bit.
        """,
        verilog="`y = en << a` doesn't translate directly; build the vector explicitly.",
        task="When `en = '1'`, set exactly one bit of `y`: `y(i) = '1'` for input `a = i`. When `en = '0'`, all bits are `'0'`.",
        ports="a: in slv(2:0); en: in sl; y: out slv(7:0)",
        numeric=True,
        hints=["Default all zeros, then set one bit inside `if en = '1'`."],
    ),
    dict(
        num=5, name="seven_seg",
        concept="lookup tables via `case` or a constant array.",
        intro="""
            A lookup table is a `case` with one row per input value, or a constant array
            indexed by the input:

            ```vhdl
            type lut_t is array (0 to 3) of std_logic_vector(2 downto 0);
            constant LUT : lut_t := ("001", "011", "111", "110");
            ...
            pattern <= LUT(to_integer(unsigned(code)));
            ```

            The seven segments of a display are named `a` to `g`:

            ```
                 aaa
                f   b
                f   b
                 ggg
                e   c
                e   c
                 ddd
            ```

            Many boards (Nexys, Basys) drive segments **active-low**: `'0'` lights a segment.
        """,
        verilog="A `case` in `always @(*)`, or a `localparam` array. VHDL needs an array `type` declaration first.",
        task="""
            Convert the hex digit `hex` (0–F) to a 7-segment pattern, **active-low**, with bit
            order `seg(6 downto 0) = g f e d c b a`.

            Use the standard hex glyphs: `6` includes the top segment, `7` lights only
            `a`, `b`, `c`, `9` includes the bottom segment, and `b` and `d` are lowercase.
            `A`, `C`, `E`, `F` are uppercase.
        """,
        ports="hex: in slv(3:0); seg: out slv(6:0)",
        numeric=True,
        hints=[
            "Work out the active-high pattern for each digit first (e.g. `1` lights `b` and `c`: `\"0000110\"`), then invert.",
            "`0` lights every segment except `g`.",
        ],
    ),
    dict(
        num=6, name="kmap4",
        concept="from truth table to minimal logic.",
        intro="""
            A Karnaugh map arranges a truth table so that adjacent cells differ in one input.
            Groups of 1, 2, 4 or 8 adjacent 1s become single product terms. Rows and columns
            are in Gray-code order, and the map wraps around at the edges.

            Minimize by hand first, then write the expression. (Synthesis would minimize a
            truth table for you, but reading K-maps is still a core skill, and a minimal
            expression is easier to review.)
        """,
        verilog="Same exercise; just remember VHDL's parentheses rule.",
        task="""
            `y = Σm(1, 3, 4, 5, 7, 9, 13, 15)` over inputs `a b c d` (`a` is the MSB of the
            minterm number). The K-map, rows `ab`, columns `cd`:

            | ab \\ cd | 00 | 01 | 11 | 10 |
            |---|---|---|---|---|
            | **00** | 0 | 1 | 1 | 0 |
            | **01** | 1 | 1 | 1 | 0 |
            | **11** | 0 | 1 | 1 | 0 |
            | **10** | 0 | 1 | 0 | 0 |
        """,
        ports="a, b, c, d: in sl; y: out sl",
        hints=[
            "Look for a group of 4 in the column pattern first, then cover the stragglers.",
            "Four product terms. Three of them are groups of four; the last covers just a pair.",
        ],
    ),
    dict(
        num=7, name="magnitude_cmp", numeric=True,
        concept="comparators from `numeric_std` vs. by hand.",
        intro="""
            With `numeric_std` a comparator is one line per flag. Try writing it both ways:
            once with `unsigned` comparisons, and once by hand (an MSB-first chain: the first
            bit position where the inputs differ decides).
        """,
        verilog="`a > b` on vectors is numeric in Verilog; in VHDL, cast to `unsigned` first.",
        task="Compare the 4-bit unsigned `a` and `b`: `gt`, `eq`, `lt`.",
        ports="a, b: in slv(3:0); gt, eq, lt: out sl",
        hints=["Exactly one of the three outputs is `'1'` at a time."],
    ),
    dict(
        num=8, name="bcd_add_digit", numeric=True,
        concept="add-6 correction.",
        intro="""
            Adding two BCD digits in binary gives 0–19. Results above 9 aren't valid BCD:
            adding 6 skips the six unused codes (`1010`–`1111`), wrapping the digit into
            range and producing a decimal carry.

            ```
              7 + 5 = 12 = 0b01100 → too big → 12 + 6 = 18 = 0b1_0010 → digit 2, carry 1
            ```
        """,
        verilog="Same arithmetic; widen to 5 bits before adding.",
        task="Add two BCD digits `a`, `b` and the carry-in `cin` (inputs are always valid BCD 0–9). Output the BCD digit `s` and carry-out `cout`.",
        ports="a, b: in slv(3:0); cin: in sl; s: out slv(3:0); cout: out sl",
        options={"range": {"a": [0, 9], "b": [0, 9]}},
        after_ports="The grader only drives 0–9 on `a` and `b`.",
        hints=["5-bit binary sum; if it's above 9, add 6 and set `cout`."],
    ),
    dict(
        num=9, name="mux2_wide",
        concept="wide muxes are still one line.",
        intro="""
            `when ... else` works on vectors of any width, so a 100-bit mux reads exactly like
            a 1-bit one.
        """,
        verilog="`sel ? b : a` becomes `b when sel = '1' else a`.",
        task="100-bit 2-to-1 mux: `y = b` when `sel = '1'`, else `a`.",
        ports="a, b: in slv(99:0); sel: in sl; y: out slv(99:0)",
        hints=["One line."],
    ),
    dict(
        num=10, name="mux9_default",
        concept="`when others` producing a non-zero default.",
        intro="""
            `when others` doesn't have to output zero. Here it covers seven unused select
            codes at once.

            `(others => '1')` is a convenient all-ones value whose width comes from the target.
        """,
        verilog="`default: y = '1;` (SystemVerilog fill) becomes `when others => y <= (others => '1');`.",
        task="A 9-to-1 mux of 16-bit inputs (`sel` 0–8 picks `d0`–`d8`). For `sel` 9–15, output all ones.",
        ports="sel: in slv(3:0); d0, d1, d2, d3, d4, d5, d6, d7, d8: in slv(15:0); y: out slv(15:0)",
        hints=["A `case` with nine choices plus `when others`."],
    ),
    dict(
        num=11, name="adder100_numeric", numeric=True,
        concept="compare with 4.11. One line with `numeric_std` gives the same hardware.",
        intro="""
            Synthesis tools recognize `+` and build an adder using the FPGA's dedicated carry
            chain, which is faster than a generic ripple of LUTs. A 100-bit add with
            carry-in and carry-out is a single expression if you widen by one bit:

            ```vhdl
            wide <= ('0' & unsigned(x)) + unsigned(z) + ci;    -- VHDL-2008: unsigned + std_logic
            ```
        """,
        verilog="`assign {cout, sum} = a + b + cin;` maps to a 101-bit `unsigned` sum.",
        task="100-bit add with carry-in and carry-out: `{cout, sum} = a + b + cin`.",
        ports="a, b: in slv(99:0); cin: in sl; sum: out slv(99:0); cout: out sl",
        hints=["A 101-bit intermediate signal, then slice it."],
    ),
    dict(
        num=12, name="kmap_dontcare",
        concept="using don't-cares to simplify.",
        intro="""
            A **don't-care** is an input combination that never occurs (or whose output nobody
            reads). On a K-map you may treat each one as 0 or 1, whichever makes bigger groups.

            The grader skips the don't-care inputs, so any choice for them passes.
        """,
        verilog="Same exercise.",
        task="""
            `y = Σm(2, 3, 5, 7, 11, 13) + d(0, 1, 15)` over `a b c d` (`a` = MSB).

            | ab \\ cd | 00 | 01 | 11 | 10 |
            |---|---|---|---|---|
            | **00** | x | x | 1 | 1 |
            | **01** | 0 | 1 | 1 | 0 |
            | **11** | 0 | 1 | x | 0 |
            | **10** | 0 | 0 | 1 | 0 |
        """,
        ports="a, b, c, d: in sl; y: out sl",
        options={"dont_care": "(a << 3 | b << 2 | c << 1 | d) in (0, 1, 15)"},
        hints=[
            "Using 0, 1 and 15 as 1s gives groups of four.",
            "Three product terms of two literals each.",
        ],
    ),
    dict(
        num=13, name="sop_and_pos",
        concept="two forms of the same function.",
        intro="""
            A **sum of products** (SOP) groups the 1s on a K-map; a **product of sums** (POS)
            groups the 0s and writes each group as an OR term, then ANDs them. Both describe
            the same function, and for some functions one form is much smaller than the other.
        """,
        verilog="Same exercise.",
        task="""
            For `f = Σm(0, 2, 6, 7, 8, 10, 14, 15)` over `a b c d` (`a` = MSB), output the
            minimal sum-of-products on `y_sop` and the minimal product-of-sums on `y_pos`.
            Both are checked against `f`.

            Write both forms by hand from the K-map before coding them.
        """,
        ports="a, b, c, d: in sl; y_sop, y_pos: out sl",
        hints=[
            "Notice that `a` doesn't matter at all.",
            "Each minimal form has two terms.",
        ],
    ),
    dict(
        num=14, name="truth_table3",
        concept="implementing from a table.",
        intro="""
            When a function is given as a table, a `case` on the concatenated inputs is a
            direct translation. To `case` on several signals, concatenate them into a
            variable or signal first; VHDL-2008 also allows a qualified expression:

            ```vhdl
            case std_logic_vector'(x & z) is
              when "00" => ...
            ```
        """,
        verilog="`case ({a,b,c})` needs a typed vector in VHDL: qualify the concatenation or use a helper signal.",
        task="""
            Implement this truth table:

            | a | b | c | y |
            |---|---|---|---|
            | 0 | 0 | 0 | 1 |
            | 0 | 0 | 1 | 0 |
            | 0 | 1 | 0 | 1 |
            | 0 | 1 | 1 | 1 |
            | 1 | 0 | 0 | 0 |
            | 1 | 0 | 1 | 0 |
            | 1 | 1 | 0 | 1 |
            | 1 | 1 | 1 | 0 |
        """,
        ports="a, b, c: in sl; y: out sl",
        hints=["Either a `case` on `a & b & c`, or minimize and write the gates."],
    ),
    dict(
        num=15, name="wave_puzzle_comb1",
        concept="reverse-engineering logic from a waveform.",
        intro="""
            Sometimes all you have is a simulation trace. Collect the samples into a truth
            table (sort them by input), then minimize as usual.
        """,
        verilog="Nothing language-specific here.",
        task="Find the combinational circuit that produced this trace:\n\n" + PUZZLE1_TABLE,
        ports="a, b, c: in sl; q: out sl",
        hints=["Sort the rows by `abc`, then draw a 3-input K-map."],
    ),
    dict(
        num=16, name="wave_puzzle_comb2",
        concept="reverse-engineering a 4-input function.",
        intro="""
            Same idea with four inputs. Look for structure: is `q` sometimes just a copy or the
            inverse of one input?
        """,
        verilog="Nothing language-specific here.",
        task="Find the combinational circuit that produced this trace:\n\n" + PUZZLE2_TABLE,
        ports="a, b, c, d: in sl; q: out sl",
        hints=[
            "Compare the rows with `a = 0` to those with `a = 1`.",
            "The answer has a compact form using XOR.",
        ],
    ),
    dict(
        num=17, name="wave_puzzle_vec", numeric=True,
        concept="when there's no formula, the table *is* the design.",
        intro="""
            Some functions have no simple formula: the trace is the only specification. A
            constant array indexed by the input reproduces it exactly.
        """,
        verilog="A `localparam` lookup array; in VHDL, declare an array type and a constant.",
        task="Reproduce this trace exactly:\n\n" + PUZZLE_VEC_TABLE,
        ports="x: in slv(3:0); q: out slv(3:0)",
        hints=["Sort the samples by `x` and write a 16-entry constant array or `case`."],
    ),
    dict(
        num=18, name="odd_parity9",
        concept="generating and checking a parity bit.",
        intro="""
            With **odd** parity, the parity bit is chosen so that the data bits plus the
            parity bit contain an odd number of 1s. A receiver checks the whole word: an even
            count means a bit flipped somewhere.
        """,
        verilog="`~^data` is `not (xor data)` (VHDL-2008 also has `xnor data`).",
        task="""
            - `pbit`: the odd-parity bit for the 8 data bits in `data`
            - `err`: `'1'` when the 9-bit received `word` (data plus parity) does **not** have odd parity
        """,
        ports="data: in slv(7:0); word: in slv(8:0); pbit, err: out sl",
        hints=["Both outputs are a reduction plus possibly a `not`."],
    ),
    dict(
        num=19, name="onehot_to_bin", numeric=True,
        concept="encoding with validity checking.",
        intro="""
            Converting one-hot back to binary is easy if the input is guaranteed one-hot. If
            it isn't, check first: exactly one bit set means `v /= 0` and `v and (v - 1) = 0`
            when you treat `v` as `unsigned`.
        """,
        verilog="Same bit trick; `v & (v-1)` becomes `v and (v - 1)` on `unsigned`.",
        task="Convert the one-hot 8-bit `oh` to its binary index `idx`. `valid = '0'` if `oh` is not exactly one-hot, and then `idx = 0`.",
        ports="oh: in slv(7:0); idx: out slv(2:0); valid: out sl",
        hints=["A loop that counts set bits and remembers the last index works too."],
    ),
    dict(
        num=20, name="alu4", numeric=True,
        concept="a small ALU, the bridge to a CPU datapath.",
        intro="""
            An ALU is a mux in front of several function units. Compute the selected result in
            a `case`, then derive flags from the result.

            Comparison results are one bit, zero-extended to the ALU width, as in RISC-V
            `slt`.
        """,
        verilog="Signed vs. unsigned comparisons are explicit casts here, not declarations.",
        task="""
            4-bit ALU. Results wrap at 4 bits.

            | `op` | `y` |
            |---|---|
            | `000` | `a + b` |
            | `001` | `a - b` |
            | `010` | `a and b` |
            | `011` | `a or b` |
            | `100` | `a xor b` |
            | `101` | `"0001"` if `a < b` as **signed**, else `"0000"` |
            | `110` | `"0001"` if `a < b` as **unsigned**, else `"0000"` |
            | `111` | `b` |

            `zero` is `'1'` when `y` is `"0000"`.
        """,
        ports="a, b: in slv(3:0); op: in slv(2:0); y: out slv(3:0); zero: out sl",
        hints=["Compute `y` in a process with a variable, then `zero` from that variable (or from the output port, readable in VHDL-2008)."],
    ),
    dict(
        num=21, name="thermometer", numeric=True,
        concept="thermometer code (common in ADC/flash designs).",
        intro="""
            A **thermometer code** sets the lowest `n` bits of a vector, like mercury rising.
            Flash ADCs produce it naturally from a row of comparators.
        """,
        verilog="Nothing new; a loop or a lookup.",
        task="Convert the 3-bit value `n` to a 7-bit output `t` with the lowest `n` bits set (`n = 0` gives `\"0000000\"`, `n = 7` gives `\"1111111\"`).",
        ports="n: in slv(2:0); t: out slv(6:0)",
        hints=["`t(i) <= '1' when i < to_integer(unsigned(n)) else '0';` in a generate."],
    ),
]
