SECTION = 6

PROBLEMS = [
    dict(
        num=1, name="unsigned_add", numeric=True,
        concept="`ieee.numeric_std`, converting `slv ↔ unsigned`, `resize`. Never use `std_logic_arith`.",
        intro="""
            `std_logic_vector` is just a bag of bits: it has no arithmetic. `ieee.numeric_std`
            adds two types with the same elements but numeric meaning, `unsigned` and
            `signed`, plus the operators and conversions:

            ```vhdl
            use ieee.numeric_std.all;
            ...
            total <= std_logic_vector(unsigned(x) + unsigned(z));    -- slv -> unsigned -> slv
            wider <= resize(unsigned(x), 12);                        -- zero-extend to 12 bits
            ```

            Converting between `std_logic_vector` and `unsigned`/`signed` is a plain type
            conversion because they're closely related array types. The result of `+` is as
            wide as the wider operand, so to keep a carry you widen an operand *first*.

            You'll see `ieee.std_logic_arith` and `std_logic_unsigned` in old code. They're
            vendor packages, not IEEE standards; don't use them in new designs.
        """,
        verilog="Verilog vectors are implicitly unsigned numbers. In VHDL you choose `unsigned` or `signed` explicitly, and widths never grow automatically.",
        task="Add the two 8-bit unsigned numbers `a` and `b` and output the full 9-bit result (including the carry) on `sum`.",
        ports="a, b: in slv(7:0); sum: out slv(8:0)",
        hints=[
            "`resize(unsigned(a), 9) + unsigned(b)` is 9 bits wide.",
            "Convert back with `std_logic_vector(...)`.",
        ],
    ),
    dict(
        num=2, name="signed_compare", numeric=True,
        concept="the same bits compare differently as `signed` vs. `unsigned`.",
        intro="""
            `x"FF"` is 255 as `unsigned` and −1 as `signed`. Comparisons use the type you
            give them:

            ```vhdl
            neg_bigger <= '1' when signed(p) > signed(q) else '0';
            ```

            The result of a comparison is a `boolean`, so turn it into `std_logic` with
            `when ... else`.
        """,
        verilog="In Verilog, a comparison is signed only if *both* operands are declared `signed`. In VHDL the operand types decide, and mixing `signed` with `unsigned` is a compile error.",
        task="""
            Treat `a` and `b` as signed. Set flags `lt` (a < b), `eq`, and `gt`, and output
            `min_s`, the signed minimum. Also output `lt_u`, an **unsigned** `a < b`, to show
            the difference.
        """,
        ports="a, b: in slv(7:0); lt, eq, gt, lt_u: out sl; min_s: out slv(7:0)",
        options={"copy": [["b", "a", 0.1]]},
        hints=["`lt <= '1' when signed(a) < signed(b) else '0';`"],
    ),
    dict(
        num=3, name="signed_overflow", numeric=True,
        concept="two's-complement overflow detection.",
        intro="""
            Adding two `signed` values of the same width wraps around silently. Overflow
            happens exactly when both operands have the same sign and the result's sign is
            different. (Equivalently: compute one bit wider and check whether the top two bits
            of the wide result disagree.)

            ```vhdl
            -- sign bits of operands and result
            wrapped <= (x(7) and z(7) and not r(7)) or (not x(7) and not z(7) and r(7));
            ```
        """,
        verilog="Same rule as in Verilog; here `+` on two 8-bit `signed` gives an 8-bit result.",
        task="`s = a + b` (8-bit signed, wrapping). `ovf = '1'` when the true sum doesn't fit in 8 signed bits.",
        ports="a, b: in slv(7:0); s: out slv(7:0); ovf: out sl",
        hints=["Compare the sign bits of `a`, `b`, and the 8-bit sum."],
    ),
    dict(
        num=4, name="popcount", numeric=True,
        concept="a `variable` counter inside a combinational process with a `for` loop.",
        intro="""
            A variable can be an `integer` or `unsigned` counter that a loop increments. Each
            iteration becomes an adder stage in hardware.

            ```vhdl
            process(all)
              variable n : unsigned(2 downto 0);
            begin
              n := (others => '0');
              for i in flags'range loop
                if flags(i) = '1' then n := n + 1; end if;
              end loop;
              num_flags <= std_logic_vector(n);
            end process;
            ```

            `unsigned + integer` is defined in `numeric_std`, so `n + 1` works.
        """,
        verilog="Same as a `for` loop in `always @(*)` with a blocking counter.",
        task="Output on `count` the number of `'1'` bits in `din`.",
        ports="din: in slv(7:0); count: out slv(3:0)",
        hints=["A 4-bit variable is enough: the count is at most 8."],
    ),
    dict(
        num=5, name="mux256", numeric=True,
        concept="`to_integer(unsigned(sel))` as an array index.",
        intro="""
            Indices are integers. Convert a vector to an integer to use it as an index:

            ```vhdl
            bit_out <= mask(to_integer(unsigned(addr)));
            ```

            Synthesis turns a variable index into a mux.
        """,
        verilog="`din[sel]` needs `to_integer(unsigned(sel))` as the index.",
        task="Output on `y` the bit of `din` selected by `sel`: `y = din(sel)`.",
        ports="din: in slv(255:0); sel: in slv(7:0); y: out sl",
        hints=["One line."],
    ),
    dict(
        num=6, name="mux256x4", numeric=True,
        concept="computed slice ranges, `din(4*i+3 downto 4*i)`.",
        intro="""
            Slice bounds can be expressions. With an integer index, a fixed-width field is
            `v(W*i + W - 1 downto W*i)`:

            ```vhdl
            byte_out <= mem_word(8 * k + 7 downto 8 * k);    -- k is an integer
            ```

            The *width* of the slice must be constant (here 8), even though its position
            varies. A process with an `integer` variable keeps it readable.
        """,
        verilog="`din[sel*4 +: 4]` becomes `din(4*i + 3 downto 4*i)` with `i := to_integer(unsigned(sel))`.",
        task="`din` packs 256 4-bit values: value `i` is `din(4*i+3 downto 4*i)`. Output on `y` the one selected by `sel`.",
        ports="din: in slv(1023:0); sel: in slv(7:0); y: out slv(3:0)",
        hints=["In a `process(all)`: `variable i : natural range 0 to 255;` then `i := to_integer(unsigned(sel));`."],
    ),
    dict(
        num=7, name="resize_signed", numeric=True,
        concept="`resize` on `signed` does sign extension, on `unsigned` it zero-extends, and narrowing truncates.",
        intro="""
            `resize(x, n)` picks its behavior from the type of `x`:

            | call | effect when widening |
            |---|---|
            | `resize(unsigned(v), n)` | pad with zeros |
            | `resize(signed(v), n)`   | copy the sign bit |

            When narrowing, `resize` on `unsigned` keeps the low bits. On `signed` it keeps the
            sign bit **and** the low bits, which is rarely what you want. To truncate, take a
            slice instead.
        """,
        verilog="`{{8{x[7]}}, x}` becomes `resize(signed(x), 16)`.",
        task="""
            - `ext_s`: `din` sign-extended from 8 to 16 bits
            - `ext_u`: `din` zero-extended from 8 to 16 bits
            - `trunc`: the low 4 bits of `din`
        """,
        ports="din: in slv(7:0); ext_s, ext_u: out slv(15:0); trunc: out slv(3:0)",
        hints=["`ext_s <= std_logic_vector(resize(signed(din), 16));`"],
    ),
    dict(
        num=8, name="enum_decoder", numeric=True,
        concept="user-defined enumerated `type` inside an architecture, then decoding it to outputs.",
        intro="""
            An **enumerated type** names its values. The tools choose the encoding.

            ```vhdl
            type mode_t is (OFF, LOW, HIGH);
            signal mode : mode_t;
            ...
            case mode is
              when OFF  => fan <= "00";
              when LOW  => fan <= "01";
              when HIGH => fan <= "11";
            end case;
            ```

            A `case` on an enum needs no `when others` if every value is listed. That's a nice
            property: add a value later and the compiler points to every `case` that forgot it.
        """,
        verilog="Instead of `localparam` codes, VHDL has real enumerated types. The simulator shows the names in the waveform.",
        task="""
            Declare `type stage_t is (IDLE, LOAD, RUN, DONE)` in the architecture. Decode `sel`
            into a `stage_t` signal (0 → IDLE … 3 → DONE). Then drive the outputs from the
            enum with a `case`: `busy` is `'1'` in LOAD or RUN, and `fin` is `'1'` in DONE.
        """,
        ports="sel: in slv(1:0); busy, fin: out sl",
        hints=[
            "`stage_t'val(to_integer(unsigned(sel)))` converts an integer position to the enum value, or use a `case` on `sel`.",
            "`when LOAD | RUN =>` groups two values.",
        ],
    ),
    dict(
        num=9, name="integer_range", numeric=True,
        concept="internal `integer range 0 to 99` signals and saturating logic.",
        intro="""
            An `integer` signal with a range constraint synthesizes to just enough bits, and
            the simulator checks the range: assigning 100 to a `range 0 to 99` signal is a
            runtime error. That catches bugs early.

            ```vhdl
            signal level : integer range 0 to 15;
            ...
            level <= to_integer(unsigned(raw));
            out_v <= std_logic_vector(to_unsigned(level, 4));
            ```
        """,
        verilog="No equivalent: Verilog integers are just 32-bit regs. VHDL range-checks them in simulation.",
        task="""
            Convert `a` and `b` to integers, add them, saturate at 99, and output the result as
            a 7-bit unsigned value on `s`. Inputs are always 0–99.
        """,
        ports="a, b: in slv(6:0); s: out slv(6:0)",
        options={"range": {"a": [0, 99], "b": [0, 99]}},
        after_ports="The grader only drives values from 0 to 99.",
        hints=[
            "The raw sum needs a bigger range than 0 to 99 (up to 198), so use a variable or signal with `range 0 to 198` for it.",
            "`to_unsigned(n, 7)` converts back.",
        ],
    ),
    dict(
        num=10, name="abs_value", numeric=True,
        concept="the edge case at the most negative value.",
        intro="""
            `abs` is defined for `signed`, but the result has the same width as the input, and
            +128 doesn't fit in 8 signed bits: `abs(signed'(x"80"))` is `x"80"` again (−128).
            Read as an **unsigned** number, though, those bits are 128, which is the right answer.

            So computing the magnitude as `unsigned(abs(x))` works for every input. Checking
            the edge case is a habit worth building whenever you negate.
        """,
        verilog="Same wraparound as Verilog's `-x` on 8 bits.",
        task="`a` is 8-bit signed. Output `mag = |a|` as an 8-bit **unsigned** value (so −128 gives 128), and `neg` = `'1'` when `a` is negative.",
        ports="a: in slv(7:0); mag: out slv(7:0); neg: out sl",
        hints=["`std_logic_vector(abs(signed(a)))` already gives the right bits for −128."],
    ),
    dict(
        num=11, name="mult_u", numeric=True,
        concept="`*` result width is the sum of the operand widths.",
        intro="""
            `unsigned * unsigned` returns a result as wide as both operands combined, so an
            8×8 product is 16 bits with no resizing needed:

            ```vhdl
            area <= std_logic_vector(unsigned(w) * unsigned(h));
            ```

            (Contrast with `+`, which does *not* grow.)
        """,
        verilog="In Verilog the target width decides; in VHDL the operands do, and the target must match exactly.",
        task="Multiply the 8-bit unsigned `a` and `b` into the 16-bit product `p`.",
        ports="a, b: in slv(7:0); p: out slv(15:0)",
        hints=["One line."],
    ),
    dict(
        num=12, name="mult_s", numeric=True,
        concept="signed multiplication.",
        intro="""
            `signed * signed` also returns the combined width, and handles the signs for you.
            Don't multiply as `unsigned` and fix up afterward.
        """,
        verilog="`$signed(a) * $signed(b)` is `signed(a) * signed(b)`.",
        task="Multiply the 8-bit signed `a` and `b` into the 16-bit signed product `p`.",
        ports="a, b: in slv(7:0); p: out slv(15:0)",
        hints=["Same as 6.11 with `signed`."],
    ),
    dict(
        num=13, name="barrel_shifter", numeric=True,
        concept="`shift_left`/`shift_right` with a `to_integer` amount.",
        intro="""
            `numeric_std` provides `shift_left(x, n)` and `shift_right(x, n)`. `shift_right`
            on `unsigned` fills with zeros; on `signed` it copies the sign bit (an arithmetic
            shift).

            ```vhdl
            scaled <= std_logic_vector(shift_right(signed(sample), 3));    -- divide by 8, rounding down
            ```

            The amount is a `natural`, so a vector amount needs `to_integer(unsigned(...))`.
        """,
        verilog="`<<`, `>>`, `>>>` become `shift_left`, `shift_right` on `unsigned`, and `shift_right` on `signed`.",
        task="""
            32-bit shifter. `dir = '0'` shifts `din` left (logical), `dir = '1'` shifts right.
            When shifting right, `arith = '1'` makes the shift arithmetic (sign-filling) and
            `arith = '0'` logical. `arith` doesn't matter for left shifts. The shift amount is
            `amt` (0–31).
        """,
        ports="din: in slv(31:0); amt: in slv(4:0); dir, arith: in sl; dout: out slv(31:0)",
        hints=["Three cases: `shift_left(unsigned)`, `shift_right(unsigned)`, `shift_right(signed)`."],
    ),
    dict(
        num=14, name="sat_add_s", numeric=True,
        concept="saturating arithmetic.",
        intro="""
            DSP code often clamps instead of wrapping. One approach: add one bit wider, then
            compare the wide result against the limits.

            ```vhdl
            wide := resize(signed(x), 9) + resize(signed(z), 9);
            if wide > 127 then ...
            ```

            Comparing a `signed` with an integer literal (`wide > 127`) is defined in
            `numeric_std`.
        """,
        verilog="Same technique; widen first so the true sum is representable.",
        task="8-bit signed addition that clamps to +127/−128 instead of wrapping. `sat` is `'1'` when clamping occurred.",
        ports="a, b: in slv(7:0); s: out slv(7:0); sat: out sl",
        hints=["9-bit intermediate, then three cases: above 127, below −128, or in range."],
    ),
    dict(
        num=15, name="divmod10", numeric=True,
        concept="`/` and `mod` by a constant are synthesizable; by a variable they generally are not.",
        intro="""
            `numeric_std` defines `/`, `mod` and `rem` for `unsigned`. Synthesis tools turn
            division by a **constant** into multiply-and-shift logic, and a power of two into
            plain wiring. Division by a variable needs a real divider, which most tools refuse
            to infer combinationally (see 15.11).

            ```vhdl
            tens_digit <= resize(value / 10, 4);
            ```
        """,
        verilog="Same rule as Verilog synthesis: constant divisors only.",
        task="Output the quotient `q` and remainder `r` of the 8-bit unsigned `din` divided by 10.",
        ports="din: in slv(7:0); q: out slv(4:0); r: out slv(3:0)",
        hints=[
            "`unsigned(din) / 10` is 8 bits wide; `resize` it to 5 bits.",
            "`unsigned(din) rem 10` is also 8 bits wide.",
        ],
    ),
    dict(
        num=16, name="bin_to_bcd", numeric=True,
        concept="the double-dabble algorithm as a loop with a variable.",
        intro="""
            **Double dabble** converts binary to BCD with shifts and small additions. Keep a
            scratch register made of the BCD digits followed by the binary input. Repeat once
            per input bit:

            1. For every BCD digit that is 5 or more, add 3 to it.
            2. Shift the whole scratch register left by one.

            After the last shift the BCD digits hold the answer. In a combinational process
            this is a `for` loop over a variable, which unrolls into a fixed network of
            small adders.
        """,
        verilog="Same as a `for` loop with blocking assignments in `always @(*)`.",
        task="Convert the 8-bit binary `bin` into three BCD digits `hundreds`, `tens`, `ones`.",
        ports="bin: in slv(7:0); hundreds, tens, ones: out slv(3:0)",
        hints=[
            "Scratch register: `unsigned(19 downto 0)` = 12 BCD bits + 8 binary bits.",
            "Do the add-3 checks *before* each shift, 8 iterations in total.",
        ],
    ),
    dict(
        num=17, name="std_ulogic_note",
        concept="`std_ulogic` (unresolved) vs. `std_logic`, and multiple-driver errors caught at compile time.",
        intro="""
            `std_logic` is a *resolved* subtype of `std_ulogic`: when a signal has several
            drivers, a resolution function combines them (that's how `'Z'` buses work).
            `std_ulogic` is the same nine values **without** resolution, so a second driver is
            an error at elaboration instead of an `'X'` you find in the waveform hours later.

            ```vhdl
            signal en : std_ulogic;
            en <= a;
            en <= b;     -- error: several sources for unresolved signal "en"
            ```

            Many style guides (and the VHDL-2008 standard library) prefer `std_ulogic` and
            `std_ulogic_vector` for everything except real tri-state buses. They mix freely
            with `std_logic`, since in VHDL-2008 `std_logic_vector` is a subtype of
            `std_ulogic_vector`.
        """,
        verilog="Verilog `wire` resolves multiple drivers silently. `std_ulogic` is closer to SystemVerilog's single-driver `logic` checks.",
        task="""
            The stub uses `std_ulogic` ports and already contains a leftover driver for `y`.
            Implement `y = a OR b` with a concurrent assignment and try to compile: GHDL
            will report the second driver. Remove the leftover so `y` has exactly one.
        """,
        ports="a, b: in std_ulogic; y: out std_ulogic",
        stub="""
            library ieee;
            use ieee.std_logic_1164.all;

            entity top_module is
              port (
                a, b : in  std_ulogic;
                y    : out std_ulogic
              );
            end entity top_module;

            architecture rtl of top_module is
            begin
              -- Leftover from an earlier version of this design:
              leftover: process(all)
              begin
                y <= '0';
              end process leftover;

              -- Write y = a OR b here.

            end architecture rtl;
        """,
        hints=["A process that assigns a signal is a driver of it, whatever the assigned value."],
    ),
]
