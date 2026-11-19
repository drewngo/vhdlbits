SECTION = 3

PROBLEMS = [
    dict(
        num=1, name="vec_split",
        concept="`std_logic_vector`, `downto`, single-bit indexing.",
        intro="""
            A vector is declared with its index range. `downto` puts the highest index on the
            left, which is the usual convention for numbers (MSB first).

            ```vhdl
            signal flags : std_logic_vector(3 downto 0);
            ...
            busy <= flags(2);        -- one bit: parentheses, not brackets
            ```

            Assigning a whole vector requires the same length on both sides.
        """,
        verilog="`v[2]` becomes `v(2)`, and `[2:0]` in a declaration becomes `(2 downto 0)`.",
        task="Pass the 3-bit vector `v` through to `outv` unchanged, and also break it out into individual bits `o2`, `o1`, `o0`.",
        ports="v: in slv(2:0); outv: out slv(2:0); o2, o1, o0: out sl",
        hints=["`o0 <= v(0);` and so on."],
    ),
    dict(
        num=2, name="byte_split",
        concept="slices `x(15 downto 8)`.",
        intro="""
            A slice is a contiguous sub-range of a vector. The slice direction must match the
            declaration (`downto` for a `downto` vector).

            ```vhdl
            opcode <= word(31 downto 26);
            ```
        """,
        verilog="`x[15:8]` becomes `x(15 downto 8)`. Writing `x(8 to 15)` on a `downto` vector is a null slice, not a reversal.",
        task="Split the 16-bit `din` into its upper byte `hi` and lower byte `lo`.",
        ports="din: in slv(15:0); hi, lo: out slv(7:0)",
        hints=["Two slice assignments."],
    ),
    dict(
        num=3, name="byte_swap",
        concept="assigning to slices of an output.",
        intro="""
            A slice can also be the *target* of an assignment, which is handy when building an
            output piece by piece:

            ```vhdl
            pkt(15 downto 8) <= header;
            pkt(7 downto 0)  <= payload;
            ```
        """,
        verilog="Same as `assign y[15:8] = ...;`, without `assign`.",
        task="Reverse the byte order of the 32-bit word `din` (endianness swap): byte 0 goes to byte 3, byte 1 to byte 2, and so on.",
        ports="din: in slv(31:0); dout: out slv(31:0)",
        hints=[
            "Four slice assignments, one per byte of `dout`.",
            "Alternatively, one concatenation: `din(7 downto 0) & din(15 downto 8) & ...`.",
        ],
    ),
    dict(
        num=4, name="bitwise_vs_logical",
        concept="VHDL has no `||`. Logical tests produce `boolean`, which you have to convert to `std_logic`.",
        intro="""
            `and`/`or` on vectors are **bitwise**: they work element by element and return a
            vector. A *test* such as `v /= "000"` returns a `boolean` (`true`/`false`), which is a
            different type from `std_logic`. You can't assign a `boolean` to a `std_logic`
            signal directly; convert it with a conditional assignment:

            ```vhdl
            nonempty <= '1' when count /= "0000" else '0';
            ```

            Booleans can be combined with `and`/`or` too: `(x /= "00") or (z = "11")` is a
            boolean.
        """,
        verilog="`a || b` on vectors means \"either is nonzero\". In VHDL write the test explicitly: `(a /= \"000\") or (b /= \"000\")`, then turn the boolean into `'1'`/`'0'`.",
        task="""
            - `or_bitwise` = bitwise OR of `a` and `b`
            - `or_logical` = `'1'` if either vector is nonzero
            - `not_both` = bitwise NOT of `b` in the upper 3 bits and bitwise NOT of `a` in the lower 3 bits
        """,
        ports="a, b: in slv(2:0); or_bitwise: out slv(2:0); or_logical: out sl; not_both: out slv(5:0)",
        hints=[
            "`not` works on whole vectors, and `&` concatenates them.",
            "`or_logical <= '1' when (a /= \"000\") or (b /= \"000\") else '0';`",
        ],
    ),
    dict(
        num=5, name="reduction",
        concept="VHDL-2008 unary reduction operators (`and v`, `or v`, `xor v`).",
        intro="""
            VHDL-2008 lets you put a logical operator in front of a single vector. It folds the
            operator across every bit and returns one `std_logic`:

            ```vhdl
            all_ready <= and ready_vec;   -- '1' only if every bit is '1'
            ```

            Before 2008 you needed a loop or a function for this.
        """,
        verilog="`&v`, `|v`, `^v` become `and v`, `or v`, `xor v`.",
        task="""
            - `all_ones` is `'1'` when every bit of `v` is set
            - `any_one` is `'1'` when at least one bit is set
            - `parity` is the XOR of all bits (even parity)
        """,
        ports="v: in slv(7:0); all_ones, any_one, parity: out sl",
        hints=["Three one-liners with unary `and`, `or`, `xor`."],
    ),
    dict(
        num=6, name="concat",
        concept="`&` concatenation to build a value, then slices to break it apart.",
        intro="""
            `&` joins vectors and bits into a longer vector, left operand first (MSB side):

            ```vhdl
            word <= "10" & addr & '0';     -- 2 + 5 + 1 = 8 bits when addr is 5 bits
            ```

            Lengths have to add up exactly to the target width.
        """,
        verilog="`{a, b}` becomes `a & b`. There's no replication `{4{x}}` operator; see 3.9.",
        task="""
            Form the 32-bit value `"01" & a & b & c & d & e & f` (six 5-bit inputs, MSB first),
            then split it into four bytes: `w` is the top byte and `z` the bottom.
        """,
        ports="a, b, c, d, e, f: in slv(4:0); w, x, y, z: out slv(7:0)",
        hints=[
            "Declare a 32-bit internal signal for the concatenation.",
            "`w <= all32(31 downto 24);` etc.",
        ],
    ),
    dict(
        num=7, name="bit_reverse",
        concept="`for ... generate`, or a loop in a process. VHDL has no built-in reverse operator.",
        intro="""
            A `for ... generate` replicates concurrent statements. The loop index is a constant
            in each copy, so it can be used in index arithmetic:

            ```vhdl
            gen_inv: for i in 0 to 3 generate
              q(i) <= not d(i);
            end generate gen_inv;
            ```

            Generate statements need a label (`gen_inv:` above).
        """,
        verilog="A Verilog `generate for` with a `genvar` maps directly; VHDL needs no separate genvar declaration.",
        task="Reverse the bit order: `dout(i) = din(7-i)`.",
        ports="din: in slv(7:0); dout: out slv(7:0)",
        hints=["`dout(i) <= din(7 - i);` inside a labelled `for i in 0 to 7 generate`."],
    ),
    dict(
        num=8, name="sign_extend",
        concept="aggregates `(others => x)` and `(23 downto 0 => din(7))`.",
        intro="""
            An **aggregate** builds a vector by naming element positions:

            ```vhdl
            zeros <= (others => '0');                 -- every bit '0', any width
            mask  <= (7 downto 4 => '1', others => '0');
            ```

            The value in an aggregate can be a signal, so `(others => sel)` copies one bit
            into every position. Combined with `&`, that's sign extension.
        """,
        verilog="`{24{din[7]}}` replication becomes `(23 downto 0 => din(7))`.",
        task="Sign-extend the 8-bit two's-complement value `din` to 32 bits. (Section 6 revisits this with `resize` on `signed`.)",
        ports="din: in slv(7:0); dout: out slv(31:0)",
        hints=[
            "Upper 24 bits are all copies of `din(7)`.",
            "Inside a concatenation an `others` aggregate has no known width, so use an explicit range: `(23 downto 0 => din(7)) & din`. Or assign the two slices of `dout` separately.",
        ],
    ),
    dict(
        num=9, name="pattern_fill",
        concept="building a vector by repeated concatenation or a generate loop.",
        intro="""
            Without a replication operator, short repeats are just written out with `&`, and
            longer ones use a generate loop over slices:

            ```vhdl
            g: for i in 0 to 7 generate
              wide(2*i+1 downto 2*i) <= pair;
            end generate g;
            ```
        """,
        verilog="`{4{pat}}` has no direct equivalent.",
        task="`dout` is the 4-bit input `pat` repeated four times.",
        ports="pat: in slv(3:0); dout: out slv(15:0)",
        hints=["`pat & pat & pat & pat` works. Try the generate-loop version too."],
    ),
    dict(
        num=10, name="nibble_swap",
        concept="concatenating two slices of the same vector.",
        intro="""
            Slices of one signal can be reordered in a single concatenation:

            ```vhdl
            rotated <= v(0) & v(7 downto 1);   -- rotate right by one
            ```
        """,
        verilog="`{din[3:0], din[7:4]}` becomes `din(3 downto 0) & din(7 downto 4)`.",
        task="Swap the two 4-bit halves of the byte `din`.",
        ports="din: in slv(7:0); dout: out slv(7:0)",
        hints=["One concatenation."],
    ),
    dict(
        num=11, name="wide_reduce",
        concept="reductions on long vectors.",
        intro="""
            Unary reductions work on any width, so a 100-input gate is still one line.
            Synthesis builds a tree of smaller gates for you.
        """,
        verilog="Same as `&din`, `|din`, `^din`.",
        task="Output the AND, OR and XOR reductions of the 100-bit `din` on `r_and`, `r_or`, `r_xor`.",
        ports="din: in slv(99:0); r_and, r_or, r_xor: out sl",
        hints=["Three one-liners."],
        options={"bias": {"din": 0.97}, "value_bias": {"din": [[0, 0.05], ["FFFFFFFFFFFFFFFFFFFFFFFFF", 0.1]]}},
        after_ports="The grader biases `din` toward all-ones so that `r_and` actually gets exercised.",
    ),
    dict(
        num=12, name="neighbor_xor",
        concept="index arithmetic with wraparound in a generate loop.",
        intro="""
            Generate indices are integers, so the usual integer operators work: `+`, `-`, `*`,
            `mod`, `rem`. `mod` always returns a result with the sign of the divisor, which
            makes it the right choice for wraparound:

            ```vhdl
            g: for i in 0 to 7 generate
              prev_bit(i) <= v((i + 7) mod 8);    -- neighbour to the right, wrapping
            end generate g;
            ```
        """,
        verilog="Same idea as a `genvar` loop; `%` is `mod` (or `rem`).",
        task="`y(i) = din(i) XOR din((i+1) mod 16)` for every bit.",
        ports="din: in slv(15:0); y: out slv(15:0)",
        hints=["Bit 15's neighbour is bit 0."],
    ),
    dict(
        num=13, name="wide_bitwise",
        concept="bitwise ops on wide vectors are a single line.",
        intro="""
            Bitwise operators on equal-length vectors produce a vector of the same length, so
            the width of the operands doesn't change the code.
        """,
        verilog="Same as Verilog, with keyword operators.",
        task="For four 64-bit inputs: `all_and = a AND b AND c AND d`, `any_or` the same with OR, and `odd = a XOR b XOR c XOR d`.",
        ports="a, b, c, d: in slv(63:0); all_and, any_or, odd: out slv(63:0)",
        hints=["Three one-liners."],
    ),
    dict(
        num=14, name="gray_encode",
        concept="shifting by slicing and concatenating.",
        intro="""
            Shifting a `std_logic_vector` by a constant is easiest with a slice and a fill bit:

            ```vhdl
            half <= '0' & v(7 downto 1);       -- logical right shift by 1
            ```

            (Section 6 introduces `shift_right` on `unsigned`.)
        """,
        verilog="`b >> 1` on a plain vector becomes `'0' & b(7 downto 1)`.",
        task="Convert binary to Gray code: `g = b XOR (b >> 1)`.",
        ports="b: in slv(7:0); g: out slv(7:0)",
        hints=["`g <= b xor ('0' & b(7 downto 1));`"],
    ),
    dict(
        num=15, name="gray_decode",
        concept="an inherently serial dependency expressed in a loop.",
        intro="""
            Some outputs depend on the *previous output bit*, not just on inputs. A `for` loop
            inside a combinational process with a **variable** handles that: variables update
            immediately, so each iteration sees the previous one's result.

            ```vhdl
            process(all)
              variable acc : std_logic;
            begin
              acc := '0';
              for i in v'high downto 0 loop
                acc := acc or v(i);
                seen(i) <= acc;          -- '1' from the highest set bit downward
              end loop;
            end process;
            ```

            Section 5 covers processes properly; for now, `process(all)` means "re-run whenever
            any input changes" and the loop unrolls into a chain of gates.
        """,
        verilog="It's like an `always @(*)` with a blocking-assignment loop.",
        task="""
            Convert Gray code back to binary. The MSB passes through unchanged; each lower
            binary bit is the XOR of the Gray bit with the binary bit above it:
            `b(i) = b(i+1) XOR g(i)`.
        """,
        ports="g: in slv(7:0); b: out slv(7:0)",
        hints=[
            "Iterate from bit 7 down to 0, carrying the running XOR in a variable.",
            "Equivalently, `b(i)` is the XOR of `g(7 downto i)`, so a generate with `xor g(7 downto i)` works too.",
        ],
    ),
    dict(
        num=16, name="rv_itype_fields",
        concept="slicing a real instruction format.",
        intro="""
            RISC-V instructions are fixed 32-bit words with fields at fixed positions. Decoding
            them is pure slicing. The I-type format:

            ```
            31        20 19   15 14  12 11    7 6      0
            [ imm[11:0] ][ rs1  ][funct3][  rd  ][ opcode ]
            ```

            The immediate is a 12-bit two's-complement value and is sign-extended to 32 bits.
        """,
        verilog="Same field extraction, with `downto` slices and aggregate-based sign extension.",
        task="""
            Split the I-type instruction `instr` into `opcode` [6:0], `rd` [11:7], `funct3`
            [14:12], `rs1` [19:15], and `imm`, which is bits [31:20] sign-extended to 32 bits.
        """,
        ports="instr: in slv(31:0); opcode: out slv(6:0); rd, rs1: out slv(4:0); funct3: out slv(2:0); imm: out slv(31:0)",
        hints=["`imm <= (19 downto 0 => instr(31)) & instr(31 downto 20);`"],
    ),
    dict(
        num=17, name="rv_rtype_pack",
        concept="concatenation to build a field-packed word.",
        intro="""
            Packing is the reverse of slicing: concatenate the fields in MSB-to-LSB order. The
            R-type layout:

            ```
            31     25 24  20 19  15 14  12 11   7 6      0
            [ funct7 ][ rs2 ][ rs1 ][funct3][ rd ][ opcode ]
            ```
        """,
        verilog="`{funct7, rs2, rs1, funct3, rd, opcode}` becomes a chain of `&`.",
        task="Assemble the R-type instruction `instr` from `funct7`, `rs2`, `rs1`, `funct3`, `rd`, `opcode`.",
        ports="funct7: in slv(6:0); rs2, rs1, rd: in slv(4:0); funct3: in slv(2:0); opcode: in slv(6:0); instr: out slv(31:0)",
        hints=["7 + 5 + 5 + 3 + 5 + 7 = 32."],
    ),
    dict(
        num=18, name="literals",
        concept="bit-string literals `x\"A5\"`, `b\"1010\"`, `o\"17\"`, and VHDL-2008 sized literals `12x\"ABC\"`.",
        intro="""
            Vector constants can be written in several bases:

            | literal | bits |
            |---|---|
            | `"1010"` or `b"1010"` | binary, 4 bits |
            | `x"A5"` | hex, 4 bits per digit = 8 bits |
            | `o"17"` | octal, 3 bits per digit = 6 bits |
            | `12x"ABC"` | VHDL-2008: hex digits, sized to 12 bits |
            | `10x"0F"` | sized: zero-padded on the left to 10 bits |
            | `x"1_0"` | underscores are ignored, for readability |

            The literal's length must match whatever it's compared with or assigned to.
            `(others => '1')` is the width-independent way to write all ones, but it can't be
            used directly as a comparison operand because its width is unknown there.
        """,
        verilog="`8'hA5` becomes `x\"A5\"`, and `12'hABC` becomes `12x\"ABC\"`.",
        task="""
            - `is_zero`: `din` equals 0
            - `is_a5`: `din` equals `x"A5"`
            - `is_max`: `din` is all ones
            - `masked` = `din AND x"0F"`
        """,
        ports="din: in slv(7:0); is_zero, is_a5, is_max: out sl; masked: out slv(7:0)",
        hints=[
            "Each flag is a `'1' when ... else '0'` conditional assignment.",
            "For all ones, `x\"FF\"` works here; `and din` (3.5) is a width-independent alternative.",
        ],
    ),
]
