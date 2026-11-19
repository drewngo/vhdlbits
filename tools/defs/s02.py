SECTION = 2

PROBLEMS = [
    dict(
        num=1, name="wire",
        concept="`<=` is the concurrent assignment; there is no `assign`.",
        intro="""
            A concurrent signal assignment in the architecture body is a permanent connection.
            Whenever the right-hand side changes, the left-hand side updates.

            ```vhdl
            led_green <= sensor_ok;
            ```

            Output ports can be assigned but (before VHDL-2008) not read. In VHDL-2008 you
            may read an `out` port inside the architecture, which GHDL with `--std=08` allows.
        """,
        verilog="`assign y = a;` becomes `y <= a;`. There is no `assign` keyword. In VHDL `=` is only ever a comparison; variables (Section 5) are assigned with `:=`.",
        task="Connect input `a` straight to output `y`.",
        ports="a: in sl; y: out sl",
        hints=["`y <= a;`"],
    ),
    dict(
        num=2, name="fanout",
        concept="several concurrent statements; their order doesn't matter.",
        intro="""
            The statements in an architecture body are not executed top to bottom. Each one is
            its own little process that wakes up when its inputs change. Reordering them
            changes nothing.

            ```vhdl
            z <= x;     -- these two lines describe the same circuit
            w <= z;     -- in either order
            ```
        """,
        verilog="Same as several `assign`s: order is irrelevant.",
        task="`p` follows `c`, `q` and `r` both follow `a`, and `s` follows `b`.",
        ports="a, b, c: in sl; p, q, r, s: out sl",
        hints=["Four one-line assignments. Try writing them in a scrambled order to convince yourself it doesn't matter."],
    ),
    dict(
        num=3, name="notgate",
        concept="`not` is a keyword operator.",
        intro="""
            VHDL's logical operators are keywords: `not`, `and`, `or`, `nand`, `nor`, `xor`,
            `xnor`. They work on `std_logic` and, element by element, on vectors of the same length.

            ```vhdl
            led_n <= not led;
            ```
        """,
        verilog="`~a` and `!a` are both `not a`.",
        task="Output the inverse of `a` on `y`.",
        ports="a: in sl; y: out sl",
        hints=["`not` binds tighter than the binary operators, so `not a` needs no parentheses here."],
    ),
    dict(
        num=4, name="andgate",
        concept="binary operators on `std_logic`.",
        intro="""
            ```vhdl
            both_ready <= rx_ready and tx_ready;
            ```

            `std_logic` has nine values, not two. `and` handles all of them sensibly:
            `'0' and 'X'` is `'0'`, while `'1' and 'X'` is `'X'`.
        """,
        verilog="`a & b` is `a and b`. In VHDL `&` means concatenation.",
        task="`y` is `a` AND `b`.",
        ports="a, b: in sl; y: out sl",
        hints=["`y <= a and b;`"],
    ),
    dict(
        num=5, name="norgate",
        concept="VHDL has `nor`/`nand`/`xnor` keywords.",
        intro="""
            Inverted gates are operators of their own:

            ```vhdl
            any_low <= x nand y;    -- same as not (x and y)
            ```
        """,
        verilog="`~(a | b)` can be written directly as `a nor b`.",
        task="`y` is `a` NOR `b`.",
        ports="a, b: in sl; y: out sl",
        hints=["Either `a nor b` or `not (a or b)` works."],
    ),
    dict(
        num=6, name="xnorgate",
        concept="`and`, `or`, and `xor` all have equal precedence, so mixed expressions need parentheses (`a and b or c` is a compile error).",
        intro="""
            In Verilog `&` binds tighter than `|`. VHDL gives all binary logical operators the
            **same** precedence and refuses to guess, so mixing them without parentheses fails
            to compile:

            ```vhdl
            -- f <= a and b or c;      -- error
            f <= (a and b) or c;       -- ok
            ```

            A chain of the *same* operator (`a or b or c`) is fine. `nand` and `nor` can't be
            chained at all, because they aren't associative.
        """,
        verilog="`a & b | c` relies on precedence. In VHDL you must write the parentheses.",
        task="`y` is `a` XNOR `b`: `'1'` when the inputs are equal.",
        ports="a, b: in sl; y: out sl",
        hints=["There's an `xnor` keyword. As an exercise, also try `not (a xor b)`."],
    ),
    dict(
        num=7, name="internal_signals",
        concept="declaring `signal`s between `architecture` and `begin`.",
        intro="""
            Internal nets are `signal`s. They are declared in the architecture's declarative
            region, between `architecture ... is` and `begin`, and then used in the body.

            ```vhdl
            architecture rtl of demo is
              signal mid : std_logic;
            begin
              mid <= x xor z;
              out1 <= mid;
              out2 <= not mid;
            end architecture rtl;
            ```

            Every signal must have exactly one driver (one assignment statement) unless it is
            a resolved bus. More on that in 2.15.
        """,
        verilog="A `wire` declaration becomes a `signal` declaration, and it goes in a fixed place: before `begin`.",
        task="""
            `y = (a AND b) OR (c AND d)` and `y_n = NOT y`. Compute the OR result once in an
            internal signal and use it for both outputs.
        """,
        ports="a, b, c, d: in sl; y, y_n: out sl",
        hints=[
            "Declare `signal or_out : std_logic;` before `begin`.",
            "Remember the parentheses: `(a and b) or (c and d)`.",
        ],
    ),
    dict(
        num=8, name="two_gate_chip",
        concept="describing a small real chip (AND-OR pairs, like a 7458).",
        intro="""
            Real logic chips are a good exercise in naming. Give each intermediate product term
            a signal, then OR them. Several signals of the same type can share one declaration:

            ```vhdl
            signal t1, t2, t3 : std_logic;
            ```
        """,
        verilog="`wire t1, t2;` becomes `signal t1, t2 : std_logic;`.",
        task="""
            Build both halves of the chip:

            - `p1y = (p1a·p1b·p1c) + (p1d·p1e·p1f)`
            - `p2y = (p2a·p2b) + (p2c·p2d)`

            Use internal signals for the four AND terms.
        """,
        ports="p1a, p1b, p1c, p1d, p1e, p1f, p2a, p2b, p2c, p2d: in sl; p1y, p2y: out sl",
        hints=["Four AND signals, then two OR assignments. `p1a and p1b and p1c` chains fine without parentheses."],
    ),
    dict(
        num=9, name="all_gates",
        concept="many outputs from the same two inputs.",
        intro="""
            Each output is its own concurrent statement. This is a good moment to get used to
            `nand`, `nor` and `xnor` as operators.

            ```vhdl
            differ <= p xor q;
            ```
        """,
        verilog="`a & ~b` becomes `a and not b`.",
        task="""
            From `a` and `b`, produce `o_and`, `o_or`, `o_xor`, `o_nand`, `o_nor`, `o_xnor`, and
            `o_andnot` (`a AND NOT b`).
        """,
        ports="a, b: in sl; o_and, o_or, o_xor, o_nand, o_nor, o_xnor, o_andnot: out sl",
        hints=["Seven one-liners. `not` binds tighter than `and`, so `a and not b` needs no parentheses."],
    ),
    dict(
        num=10, name="xor3",
        concept="chaining a single associative operator.",
        intro="""
            A chain of one operator needs no parentheses: `a or b or c`. Only *mixing*
            operators requires them.

            ```vhdl
            any_err <= err0 or err1 or err2;
            ```
        """,
        verilog="Same as `a ^ b ^ c`.",
        task="`y = a XOR b XOR c` (`xor` chains fine without parentheses, unlike mixed operators).",
        ports="a, b, c: in sl; y: out sl",
        hints=["One line."],
    ),
    dict(
        num=11, name="mux2_gates",
        concept="a mux built only from gates, no `when`.",
        intro="""
            A 2-to-1 mux is an AND-OR structure: each data input is gated by the select (or its
            inverse), and the two products are ORed. Later you'll write muxes with `when` and
            `case`, but it helps to see the gates once.
        """,
        verilog="No `? :` operator for now; build it from `and`/`or`/`not`.",
        task="`y = b` when `s = '1'`, else `a`. Use only logical operators.",
        ports="a, b, s: in sl; y: out sl",
        hints=[
            "`(b and s)` passes `b` when `s` is high.",
            "Don't forget the parentheses around each product term.",
        ],
    ),
    dict(
        num=12, name="majority3",
        concept="sum-of-products for a voting function.",
        intro="""
            A majority voter is common in fault-tolerant designs (triple modular redundancy).
            Write the output as a sum of products: one term per pair of inputs.
        """,
        verilog="`(a&b)|(b&c)|(a&c)` needs explicit parentheses around every product.",
        task="`y` is `'1'` when at least two of the three inputs are `'1'`.",
        ports="a, b, c: in sl; y: out sl",
        hints=["Three AND terms ORed together."],
    ),
    dict(
        num=13, name="doorbell",
        concept="translating a word problem into logic.",
        intro="""
            Word problems become logic once you name every condition. Write down, for each
            output, the exact situations in which it is `'1'`, then translate *and*/*or*/*not*
            literally.
        """,
        verilog="Nothing new; just `and`/`not` with parentheses.",
        task="""
            A doorbell has a `press` button input and a `mute` switch.

            - When the button is pressed and `mute = '0'`, sound the chime (`chime = '1'`).
            - When the button is pressed and `mute = '1'`, flash the light (`light = '1'`) instead.
            - Never drive both outputs at once.
        """,
        ports="press, mute: in sl; chime, light: out sl",
        hints=["Each output is the AND of `press` with `mute` or its inverse."],
    ),
    dict(
        num=14, name="garage_light",
        concept="combining conditions with an override.",
        intro="""
            An override that forces an output off is an AND with the override's inverse,
            applied last:

            ```vhdl
            heater <= (cold and occupied) and not window_open;
            ```
        """,
        verilog="Precedence again: write every grouping explicitly.",
        task="""
            The `light` turns on when the door is open, or when motion is detected while it's
            dark. A `force_off` override turns it off regardless.
        """,
        ports="door_open, motion, dark, force_off: in sl; light: out sl",
        hints=["`(door_open or (motion and dark)) and not force_off`"],
    ),
    dict(
        num=15, name="tristate",
        concept="the nine `std_logic` values; `'Z'` (high-impedance) as a driven value.",
        intro="""
            `std_logic` is not a two-valued bit. It has nine values:

            | value | meaning |
            |---|---|
            | `'U'` | uninitialized: nothing has ever been assigned (the default start value in simulation) |
            | `'X'` | forcing unknown: e.g. two drivers fighting with `'0'` and `'1'` |
            | `'0'`, `'1'` | forcing low / high |
            | `'Z'` | high impedance: this driver is letting go of the wire |
            | `'W'`, `'L'`, `'H'` | weak unknown / low / high (pull resistors) |
            | `'-'` | don't care (for synthesis and matching comparisons) |

            The **resolution function** decides the value of a signal that has more than one
            driver. `'Z'` loses to anything, so a driver that outputs `'Z'` effectively
            disconnects. `'0'` against `'1'` gives `'X'`. That's how tri-state buses work:

            ```vhdl
            bus_line <= tx_data when tx_en = '1' else 'Z';
            ```

            `'U'` is useful when debugging: an output that stays `'U'` in the waveform was
            never assigned.

            Inside FPGAs there are no internal tri-state buffers; synthesis turns internal
            `'Z'` logic into muxes. Real `'Z'` only exists at I/O pins.
        """,
        verilog="`1'bz` is `'Z'` (uppercase; `'z'` is a different, invalid character literal for `std_logic`). The `? :` form becomes `when ... else`.",
        task="""
            `y = a` when `en = '1'`, otherwise `'Z'`. The grader compares `'Z'` exactly.

            Use a conditional assignment, which you'll meet properly in Section 5:
            `target <= value1 when condition else value2;`
        """,
        ports="a, en: in sl; y: out sl",
        hints=["`y <= a when en = '1' else 'Z';`"],
    ),
]
