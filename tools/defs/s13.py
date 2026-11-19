import textwrap

SECTION = 13

HDR = "library ieee;\nuse ieee.std_logic_1164.all;\n"


def _src(body):
    """A VHDL file: the ieee header followed by the dedented body."""
    body = textwrap.dedent(body)
    if body.startswith("\nuse "):
        body = body[1:]          # keep extra use clauses next to the ieee header
    return HDR + body

FILES_NOTE = textwrap.indent(textwrap.dedent("""
    This problem has more than one file you edit. The grader compiles every listed file,
    packages (`*_pkg.vhd`) first, then `top_module.vhd`.
"""), " " * 12)

PROBLEMS = [
    dict(
        num=1, name="package_constants", uses=["work.my_pkg.all"],
        concept="a `package` with constants, and `use work.my_pkg.all`.",
        intro="""
            A **package** collects declarations (constants, types, functions) that several
            design units share. It lives in its own file and is compiled into a library before
            anything that uses it:

            ```vhdl
            package bus_pkg is
              constant ADDR_BITS : positive := 16;
              constant RESET_VEC : std_logic_vector(15 downto 0) := x"FFF0";
            end package bus_pkg;
            ```

            A design then imports it with `use work.bus_pkg.all;` in its context clause.
        """ + FILES_NOTE,
        verilog="Closest to a header of `` `define``s or a SystemVerilog `package`. VHDL packages are typed and scoped, not textual macros.",
        task="""
            In `my_pkg.vhd`, declare `constant WIDTH : positive := 12` and
            `constant MAGIC : std_logic_vector(11 downto 0) := x"5A3"`. In `top_module.vhd`
            (which already has `use work.my_pkg.all;`), output `dout = din XOR MAGIC`.
        """,
        ports="din: in slv(11:0); dout: out slv(11:0)",
        extra={"my_pkg.vhd": _src("""
            package my_pkg is
              -- Declare WIDTH and MAGIC here.
            end package my_pkg;
        """)},
        hints=["The constants go between `package my_pkg is` and `end package`."],
    ),
    dict(
        num=2, name="package_function", uses=["work.my_pkg.all"], numeric=True,
        concept="package declaration vs. package body.",
        intro="""
            A package that contains subprograms has two parts. The **declaration** lists what
            users can see (the function's signature); the **package body** holds the
            implementation:

            ```vhdl
            package util_pkg is
              function max(a, b : integer) return integer;
            end package util_pkg;

            package body util_pkg is
              function max(a, b : integer) return integer is
              begin
                if a > b then return a; end if;
                return b;
              end function max;
            end package body util_pkg;
            ```

            Changing only the body doesn't force users of the package to recompile.
        """ + FILES_NOTE,
        verilog="Like a SystemVerilog `package` with functions, split into interface and implementation.",
        task="""
            In `my_pkg.vhd`, declare and implement
            `function popcount(v : std_logic_vector) return natural`. Use it in
            `top_module` to output the popcount of `a` on `ca` and of `b` on `cb`.
        """,
        ports="a: in slv(15:0); b: in slv(7:0); ca: out slv(4:0); cb: out slv(3:0)",
        extra={"my_pkg.vhd": _src("""
            package my_pkg is
              -- Declare popcount here.
            end package my_pkg;

            package body my_pkg is
              -- Implement popcount here.
            end package body my_pkg;
        """)},
        hints=["`ca <= std_logic_vector(to_unsigned(popcount(a), 5));`"],
    ),
    dict(
        num=3, name="record_signal", mode="seq", uses=["work.my_pkg.all"],
        concept="`record` types for grouping pipeline fields.",
        intro="""
            A **record** groups fields of different types into one object. A pipeline stage
            then becomes one signal, and one assignment moves the whole bundle forward:

            ```vhdl
            type beat_t is record
              valid : std_logic;
              last  : std_logic;
              data  : std_logic_vector(31 downto 0);
            end record;

            constant BEAT_NONE : beat_t := (valid => '0', last => '0', data => (others => '0'));

            signal s1, s2 : beat_t;
            ...
            s2 <= s1;               -- every field at once
            dout <= s2.data;        -- select a field with a dot
            ```

            Top-level ports stay plain vectors (the grader only supports those), but inside a
            design records are everywhere.
        """ + FILES_NOTE,
        verilog="SystemVerilog `struct packed` is the closest equivalent; plain Verilog has nothing like it.",
        task="""
            In `my_pkg.vhd`, declare

            ```vhdl
            type pkt_t is record
              valid : std_logic;
              addr  : std_logic_vector(3 downto 0);
              data  : std_logic_vector(7 downto 0);
            end record;
            ```

            In `top_module`, register the inputs (`v_in`, `a_in`, `d_in`) into a `pkt_t`
            stage 1 at each rising edge, then stage 1 into stage 2, and drive the outputs
            from stage 2's fields. Active-high synchronous `reset` clears both stages to all
            zeros.
        """,
        ports="clk, reset, v_in: in sl; a_in: in slv(3:0); d_in: in slv(7:0); v_out: out sl; a_out: out slv(3:0); d_out: out slv(7:0)",
        extra={"my_pkg.vhd": _src("""
            package my_pkg is
              -- Declare pkt_t here (and optionally an all-zeros constant).
            end package my_pkg;
        """)},
        hints=["`s1 <= (valid => v_in, addr => a_in, data => d_in);` builds a record from an aggregate."],
    ),
    dict(
        num=4, name="array_of_vectors", numeric=True,
        concept="declaring `type word_array is array (natural range <>) of slv(7 downto 0)`.",
        intro="""
            An **array of vectors** is a 2-D structure: an array whose elements are
            `std_logic_vector`s. Declaring the index range as `natural range <>` makes the
            type unconstrained, so each signal or variable picks its own size:

            ```vhdl
            type word_array is array (natural range <>) of std_logic_vector(15 downto 0);
            signal taps : word_array(0 to 3);
            ...
            taps(2)(15) <= '1';      -- element 2, bit 15
            ```
        """,
        verilog="Like a Verilog memory `reg [7:0] b [0:7]`, but it's a real type you can pass to functions.",
        task="""
            Unpack the 64-bit `din` into 8 bytes (byte `i` is `din(8*i+7 downto 8*i)`) held in
            an array of vectors. Output the largest byte (unsigned) on `maxv` and its index on
            `maxi`. If several bytes share the maximum, report the lowest index.
        """,
        ports="din: in slv(63:0); maxv: out slv(7:0); maxi: out slv(2:0)",
        options={"bias": {"din": 0.8}},
        after_ports="The grader biases `din` toward bytes with many 1s, so ties for the maximum are common.",
        hints=["Only replace the running maximum when a byte is strictly greater; that keeps the lowest index on ties."],
    ),
    dict(
        num=5, name="enum_attributes", numeric=True,
        concept="`'pos`, `'val`, `'high`, and `'length` attributes.",
        intro="""
            Every scalar type comes with attributes:

            | attribute | meaning |
            |---|---|
            | `T'pos(x)` | position number of value `x` (first value is 0) |
            | `T'val(n)` | the value at position `n` |
            | `T'low`, `T'high` | first and last values |
            | `T'succ(x)`, `T'pred(x)` | next / previous value (error past the ends) |

            ```vhdl
            type day_t is (MON, TUE, WED, THU, FRI);
            ...
            n := day_t'pos(WED);          -- 2
            d := day_t'val(4);            -- FRI
            ```
        """,
        verilog="No equivalent; Verilog has no enumerated types (SystemVerilog `enum` has `.next()`).",
        task="""
            Declare `type color_t is (RED, ORANGE, YELLOW, GREEN, BLUE, VIOLET)`. Map input
            index 0–5 to the color, then output on `nxt` the **next** color's index, wrapping
            `VIOLET` → `RED`. Use `'pos`, `'val` and `'high` rather than a `case` statement.
            Inputs 6 and 7 output 0.
        """,
        ports="idx: in slv(2:0); nxt: out slv(2:0)",
        hints=[
            "Guard against 6 and 7 before calling `'val`, or you'll get a runtime range error.",
            "`if c = color_t'high then` handles the wrap.",
        ],
    ),
    dict(
        num=6, name="unconstrained_ports",
        concept="unconstrained `slv` ports and `'range`/`'length` inside the architecture.",
        intro="""
            A port declared as plain `std_logic_vector` (no range) is **unconstrained**: each
            instance gets its width from whatever is connected. Inside the architecture, use
            attributes instead of fixed numbers:

            ```vhdl
            entity invert is
              port (din : in std_logic_vector; dout : out std_logic_vector);
            end entity;
            architecture rtl of invert is
            begin
              dout <= not din;
            end architecture;
            ```

            Don't assume the range is `N downto 0`: someone may connect a slice like
            `x(12 downto 5)`. Index relative to `din'low`/`din'high`.

            This problem has two files. `top_module.vhd` is already written: it instantiates
            your `rev` entity at widths 5 and 13. You only edit `rev.vhd`.
        """,
        verilog="Verilog needs a parameter for the width. VHDL can infer it from the connection.",
        task="""
            In `rev.vhd`, complete entity `rev` (unconstrained `din`/`dout`, same length) so
            that it reverses bit order for any width: the bit at `din'high` goes to
            `dout'low`, and so on. The provided `top_module` connects `a → ra` and `b → rb`.
        """,
        ports="a: in slv(4:0); b: in slv(12:0); ra: out slv(4:0); rb: out slv(12:0)",
        stub=_src("""
            -- Provided: do not edit. Edit rev.vhd instead.
            entity top_module is
              port (
                a  : in  std_logic_vector(4 downto 0);
                b  : in  std_logic_vector(12 downto 0);
                ra : out std_logic_vector(4 downto 0);
                rb : out std_logic_vector(12 downto 0)
              );
            end entity top_module;

            architecture rtl of top_module is
            begin
              u5:  entity work.rev port map (din => a, dout => ra);
              u13: entity work.rev port map (din => b, dout => rb);
            end architecture rtl;
        """),
        extra={"rev.vhd": _src("""
            entity rev is
              port (
                din  : in  std_logic_vector;
                dout : out std_logic_vector
              );
            end entity rev;

            architecture rtl of rev is
            begin
              -- Write your code here
            end architecture rtl;
        """)},
        hints=[
            "A `for i in 0 to din'length - 1 generate` loop.",
            "`dout(dout'low + i) <= din(din'high - i);`",
        ],
    ),
    dict(
        num=7, name="generic_package", numeric=True,
        concept="a package with a `generic` clause, instantiated for different widths.",
        intro="""
            VHDL-2008 packages can have generics. The generic package is a template; a
            **package instantiation** fixes the generics and creates a real package. You can
            instantiate it in an architecture's declarative region:

            ```vhdl
            package fifo_pkg is
              generic (DEPTH : positive);
              constant ADDR_BITS : natural := ...;
            end package fifo_pkg;

            -- in an architecture:
            package fifo16 is new work.fifo_pkg generic map (DEPTH => 16);
            ...
            signal ptr : unsigned(fifo16.ADDR_BITS - 1 downto 0);
            ```

            Items from an instance are reached with a selected name (`fifo16.ADDR_BITS`).
        """ + FILES_NOTE,
        verilog="No Verilog equivalent. SystemVerilog parameterized classes are the nearest idea.",
        task="""
            In `sat_pkg.vhd`, write a generic package `sat_pkg` with `generic (W : positive)`
            and a function `sat_add(a, b : signed(W - 1 downto 0)) return signed` that adds
            two `W`-bit signed values and clamps to the most positive or most negative `W`-bit
            value instead of wrapping.

            In `top_module`, instantiate it for `W = 8` and `W = 12`, and output
            `s8 = sat_add(a8, b8)` and `s12 = sat_add(a12, b12)` (all signed).
        """,
        ports="a8, b8: in slv(7:0); s8: out slv(7:0); a12, b12: in slv(11:0); s12: out slv(11:0)",
        stub=_src("""
            use ieee.numeric_std.all;

            entity top_module is
              port (
                a8, b8   : in  std_logic_vector(7 downto 0);
                s8       : out std_logic_vector(7 downto 0);
                a12, b12 : in  std_logic_vector(11 downto 0);
                s12      : out std_logic_vector(11 downto 0)
              );
            end entity top_module;

            architecture rtl of top_module is
              -- Instantiate sat_pkg twice here.
            begin
              -- Write your code here
            end architecture rtl;
        """),
        extra={"sat_pkg.vhd": _src("""
            use ieee.numeric_std.all;

            package sat_pkg is
              generic (W : positive);
              -- Declare sat_add here.
            end package sat_pkg;

            package body sat_pkg is
              -- Implement sat_add here.
            end package body sat_pkg;
        """)},
        hints=[
            "Add one bit wider; overflow happened if the top two bits of the wide sum differ.",
            "An `others` aggregate needs a known width: build the clamp value in a `signed(W - 1 downto 0)` variable.",
        ],
    ),
]
