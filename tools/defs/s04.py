SECTION = 4

HDR = "library ieee;\nuse ieee.std_logic_1164.all;\n"

MOD_A = HDR + """
-- Provided: do not edit. o = in1 AND NOT in2
entity mod_a is
  port (
    in1, in2 : in  std_logic;
    o        : out std_logic
  );
end entity mod_a;

architecture rtl of mod_a is
begin
  o <= in1 and not in2;
end architecture rtl;
"""

MOD_B = HDR + """
-- Provided: do not edit. o1 = w XOR x, o2 = y AND z
entity mod_b is
  port (
    w, x, y, z : in  std_logic;
    o1, o2     : out std_logic
  );
end entity mod_b;

architecture rtl of mod_b is
begin
  o1 <= w xor x;
  o2 <= y and z;
end architecture rtl;
"""

MY_DFF = HDR + """
-- Provided: do not edit. A rising-edge D flip-flop with no reset.
entity my_dff is
  port (
    clk, d : in  std_logic;
    q      : out std_logic
  );
end entity my_dff;

architecture rtl of my_dff is
begin
  process(clk)
  begin
    if rising_edge(clk) then
      q <= d;
    end if;
  end process;
end architecture rtl;
"""

MY_DFF8 = HDR + """
-- Provided: do not edit. Eight rising-edge D flip-flops with no reset.
entity my_dff8 is
  port (
    clk : in  std_logic;
    d   : in  std_logic_vector(7 downto 0);
    q   : out std_logic_vector(7 downto 0)
  );
end entity my_dff8;

architecture rtl of my_dff8 is
begin
  process(clk)
  begin
    if rising_edge(clk) then
      q <= d;
    end if;
  end process;
end architecture rtl;
"""

ADD16 = HDR + """use ieee.numeric_std.all;

-- Provided: do not edit. 16-bit adder with carry in and carry out.
entity add16 is
  port (
    a, b : in  std_logic_vector(15 downto 0);
    cin  : in  std_logic;
    sum  : out std_logic_vector(15 downto 0);
    cout : out std_logic
  );
end entity add16;

architecture rtl of add16 is
  signal full : unsigned(16 downto 0);
begin
  full <= ('0' & unsigned(a)) + ('0' & unsigned(b)) + cin;  -- VHDL-2008: unsigned + std_ulogic
  sum  <= std_logic_vector(full(15 downto 0));
  cout <= full(16);
end architecture rtl;
"""

REG_N = HDR + """
-- Provided: do not edit. An N-bit register with no reset.
entity reg_n is
  generic (N : positive);
  port (
    clk : in  std_logic;
    d   : in  std_logic_vector(N - 1 downto 0);
    q   : out std_logic_vector(N - 1 downto 0)
  );
end entity reg_n;

architecture rtl of reg_n is
begin
  process(clk)
  begin
    if rising_edge(clk) then
      q <= d;
    end if;
  end process;
end architecture rtl;
"""

FULL_ADDER = HDR + """
-- Provided: do not edit. One-bit full adder.
entity full_adder is
  port (
    a, b, cin : in  std_logic;
    s, cout   : out std_logic
  );
end entity full_adder;

architecture rtl of full_adder is
begin
  s    <= a xor b xor cin;
  cout <= (a and b) or (a and cin) or (b and cin);
end architecture rtl;
"""

BCD_FADD = HDR + """use ieee.numeric_std.all;

-- Provided: do not edit. One-digit BCD adder: a + b + cin, with valid BCD inputs (0-9).
entity bcd_fadd is
  port (
    a, b : in  std_logic_vector(3 downto 0);
    cin  : in  std_logic;
    s    : out std_logic_vector(3 downto 0);
    cout : out std_logic
  );
end entity bcd_fadd;

architecture rtl of bcd_fadd is
begin
  process(all)
    variable t : unsigned(4 downto 0);
  begin
    t := ('0' & unsigned(a)) + ('0' & unsigned(b)) + cin;  -- VHDL-2008: unsigned + std_ulogic
    if t > 9 then
      t := t + 6;
      cout <= '1';
    else
      cout <= '0';
    end if;
    s <= std_logic_vector(t(3 downto 0));
  end process;
end architecture rtl;
"""

PROBLEMS = [
    dict(
        num=1, name="instantiate",
        concept="direct entity instantiation `u0: entity work.mod_a port map (...)` with named association `=>`.",
        intro="""
            Every problem in this section ships one or more modules in `provided/`. The grader
            compiles them into the same library as your design, so you can use them without
            editing them.

            A **direct entity instantiation** names the library (`work` is your own design
            library), the entity, and how each of its ports connects:

            ```vhdl
            u_inv: entity work.inverter
              port map (
                din  => sensor,       -- formal (the sub-module's port) => actual (your signal)
                dout => sensor_n
              );
            ```

            Every instance needs a label (`u_inv` above). The arrow points from the
            sub-module's port name to the signal it connects to, regardless of direction.
        """,
        verilog="`mod_a u0 (.in1(a), .in2(b), .o(y));` becomes `u0: entity work.mod_a port map (in1 => a, in2 => b, o => y);`.",
        task="""
            The provided `mod_a(in1, in2: in sl; o: out sl)` computes `o = in1 AND NOT in2`.
            Instantiate it with `a → in1`, `b → in2`, and `o → y`.
        """,
        ports="a, b: in sl; y: out sl",
        provided={"mod_a.vhd": MOD_A},
        hints=["Inside the architecture body: `u0: entity work.mod_a port map (in1 => a, in2 => b, o => y);`"],
    ),
    dict(
        num=2, name="positional_map",
        concept="positional association, and why named association is safer.",
        intro="""
            A port map can also list the actuals in the order the ports were declared:

            ```vhdl
            u_inv: entity work.inverter port map (sensor, sensor_n);
            ```

            It's shorter, but if someone reorders the sub-module's ports, your design still
            compiles and is silently wrong. Use named association in real code; this problem
            is here so you can read the positional style when you meet it.
        """,
        verilog="Same trade-off as Verilog's ordered vs. `.name()` port connections.",
        task="""
            The provided `mod_b(w, x, y, z: in sl; o1, o2: out sl)` computes `o1 = w XOR x` and
            `o2 = y AND z`. Connect `a, b, c, d` to `w, x, y, z` **by position**, and `o1`/`o2`
            to `out1`/`out2`.
        """,
        ports="a, b, c, d: in sl; out1, out2: out sl",
        provided={"mod_b.vhd": MOD_B},
        hints=["`u0: entity work.mod_b port map (a, b, c, d, out1, out2);`"],
    ),
    dict(
        num=3, name="three_dffs", mode="seq",
        concept="instantiating several copies with internal signals between them.",
        intro="""
            Connect instances to each other through internal signals. Each instance needs its
            own label:

            ```vhdl
            signal s1 : std_logic;
            ...
            u_a: entity work.buf port map (i => x,  o => s1);
            u_b: entity work.buf port map (i => s1, o => z);
            ```

            Since the provided flip-flops have no reset, their outputs start as `'U'` in
            simulation. The grader treats `'U'` on both sides as a match, so that's fine here.
        """,
        verilog="Same as wiring Verilog instances with `wire`s, but the nets are `signal`s declared before `begin`.",
        task="""
            Using the provided `my_dff(clk, d: in sl; q: out sl)`, chain three flip-flops into a
            3-stage shift register: `d → q1 → q2 → q`.
        """,
        ports="clk, d: in sl; q: out sl",
        provided={"my_dff.vhd": MY_DFF},
        hints=["Two internal signals and three instances, all sharing `clk`."],
    ),
    dict(
        num=4, name="tap_select", mode="seq",
        concept="instances plus a `case`/`with-select` mux.",
        intro="""
            A **selected signal assignment** is a concurrent mux:

            ```vhdl
            with mode select
              led <= "0001" when "00",
                     "0010" when "01",
                     "0100" when "10",
                     "1000" when others;
            ```

            The choices must cover every possible value of the selector, which for a
            `std_logic_vector` includes the nine-valued combinations, hence `when others`.
            Section 5 covers this in detail.
        """,
        verilog="A `case` inside `always @(*)` or a chain of `? :`. Here a concurrent `with ... select` does the job without a process.",
        task="""
            The provided `my_dff8(clk: in sl; d: in slv(7:0); q: out slv(7:0))` is an 8-bit
            register. Chain three of them. The 2-bit `sel` chooses the output: 0 gives `d`
            itself (no delay), 1 gives the first stage, 2 the second, and 3 the third.
        """,
        ports="clk: in sl; d: in slv(7:0); sel: in slv(1:0); q: out slv(7:0)",
        provided={"my_dff8.vhd": MY_DFF8},
        hints=["Three 8-bit internal signals for the stage outputs, then `with sel select q <= ...`."],
    ),
    dict(
        num=5, name="adder32",
        concept="wiring a carry between instances.",
        intro="""
            Large adders are often built from smaller ones by passing the carry along. A port
            can connect to a slice of a signal, or to a literal for an input:

            ```vhdl
            u_lo: entity work.add8 port map (a => x(7 downto 0), b => z(7 downto 0),
                                             cin => '0', sum => s(7 downto 0), cout => c8);
            ```

            An unused output can be left unconnected with `open`: `cout => open`.
        """,
        verilog="Unconnected outputs are `.cout()` in Verilog and `cout => open` in VHDL.",
        task="""
            The provided `add16(a, b: in slv(15:0); cin: in sl; sum: out slv(15:0); cout: out sl)`
            is a 16-bit adder. Build a 32-bit adder from two of them. Tie the first `cin` to
            `'0'` and discard the final carry.
        """,
        ports="a, b: in slv(31:0); sum: out slv(31:0)",
        provided={"add16.vhd": ADD16},
        hints=["One internal carry signal links the lower `cout` to the upper `cin`."],
    ),
    dict(
        num=6, name="carry_select",
        concept="duplicating hardware to save delay.",
        intro="""
            In a ripple design the upper half has to wait for the lower half's carry. A
            **carry-select** adder computes the upper half twice in parallel, once assuming
            carry 0 and once assuming carry 1, and uses the real carry only to pick a result.
            That trades area for speed: the critical path is one 16-bit add plus a mux.

            A conditional assignment works as a vector mux:

            ```vhdl
            result <= alt when use_alt = '1' else normal;
            ```
        """,
        verilog="The final mux is `assign sum_hi = c16 ? s1 : s0;`, written with `when ... else`.",
        task="""
            Using three provided `add16`s, build a carry-select adder. The lower half adds
            normally (carry-in 0). Both possible upper halves (carry-in 0 and 1) are computed in
            parallel, and the lower half's carry-out picks between them.
        """,
        ports="a, b: in slv(31:0); sum: out slv(31:0)",
        provided={"add16.vhd": ADD16},
        hints=["Signals: the lower carry-out, and two 16-bit candidate upper sums."],
    ),
    dict(
        num=7, name="generic_map", mode="seq",
        concept="`generic map`. Generics are VHDL's parameters.",
        intro="""
            A **generic** is a constant parameter of an entity, set per instance. Generics go in
            a `generic map` before the `port map`:

            ```vhdl
            u_fifo: entity work.fifo
              generic map (DEPTH => 16)
              port map (...);
            ```

            Port widths can depend on generics, so the actual you connect must match the width
            the generic implies.
        """,
        verilog="`#(.N(4))` becomes `generic map (N => 4)`.",
        task="""
            The provided `reg_n` has `generic (N: positive)` and ports
            `(clk: in sl; d: in slv(N-1:0); q: out slv(N-1:0))`. Instantiate a 4-bit copy for
            `d4 → q4` and a 12-bit copy for `d12 → q12`.
        """,
        ports="clk: in sl; d4: in slv(3:0); q4: out slv(3:0); d12: in slv(11:0); q12: out slv(11:0)",
        provided={"reg_n.vhd": REG_N},
        hints=["Two instances of `entity work.reg_n`, each with its own `generic map (N => ...)`."],
    ),
    dict(
        num=8, name="generate_adder",
        concept="`for ... generate` with instances and a carry array signal.",
        intro="""
            A `for ... generate` can create instances too. Carries between stages are easiest
            to handle as a vector one bit longer than the adder, so that stage `i` reads
            `c(i)` and writes `c(i+1)`:

            ```vhdl
            signal c : std_logic_vector(4 downto 0);
            ...
            c(0) <= carry_in;
            g: for i in 0 to 3 generate
              u: entity work.cell port map (x => p(i), ci => c(i), co => c(i + 1), ...);
            end generate g;
            ```
        """,
        verilog="Same as a `genvar` loop containing an instance.",
        task="""
            Using the provided `full_adder(a, b, cin: in sl; s, cout: out sl)`, generate an
            8-bit ripple-carry adder. Output every stage's carry-out on `couts`, where
            `couts(7)` is the final carry.
        """,
        ports="a, b: in slv(7:0); cin: in sl; sum: out slv(7:0); couts: out slv(7:0)",
        provided={"full_adder.vhd": FULL_ADDER},
        hints=[
            "Stage 0 takes `cin`; stage `i > 0` takes `couts(i-1)`.",
            "A 9-bit internal carry vector avoids the special case for stage 0.",
        ],
    ),
    dict(
        num=9, name="add_sub",
        concept="reusing an adder for subtraction (XOR the B input, carry-in = sub).",
        intro="""
            In two's complement, `a - b = a + (not b) + 1`. So one adder does both: XOR `b`
            with the `sub` control (which inverts it when `sub = '1'`) and feed `sub` in as the
            carry-in.

            To XOR every bit of a vector with one bit, build a vector of copies:

            ```vhdl
            flipped <= v xor (v'range => inv);
            ```
        """,
        verilog="`b ^ {32{sub}}` becomes `b xor (31 downto 0 => sub)`.",
        task="""
            Using two provided `add16`s and your own XOR logic, `result = a + b` when
            `sub = '0'` and `a - b` when `sub = '1'` (32-bit, wrapping).
        """,
        ports="a, b: in slv(31:0); sub: in sl; result: out slv(31:0)",
        provided={"add16.vhd": ADD16},
        hints=["The lower adder's `cin` is `sub`, and its carry-out feeds the upper adder."],
    ),
    dict(
        num=10, name="component_decl",
        concept="the older `component` declaration style, which is still common in legacy and vendor code.",
        intro="""
            Before direct entity instantiation (VHDL-93), every sub-module had to be declared as
            a `component` in the architecture, repeating its port list. The instance then names
            the component, without `entity work.`:

            ```vhdl
            architecture rtl of top is
              component inverter is
                port (din : in std_logic; dout : out std_logic);
              end component;
            begin
              u_inv: inverter port map (din => s, dout => s_n);
            end architecture rtl;
            ```

            You'll see this in vendor IP wrappers (where the entity may be a black box at
            compile time) and older code bases. The binding to the entity happens at
            elaboration by matching names.
        """,
        verilog="Verilog never needed this; it's closest to an `extern` declaration.",
        task="Same circuit as 4.1, but declare `mod_a` as a `component` in the architecture and instantiate it without `entity work.`.",
        ports="a, b: in sl; y: out sl",
        provided={"mod_a.vhd": MOD_A},
        hints=["Copy `mod_a`'s port list into a `component mod_a is ... end component;` before `begin`."],
    ),
    dict(
        num=11, name="adder100_generate",
        concept="scaling a generate loop up.",
        intro="""
            Generate loops don't care about size. Use the vectors' attributes to avoid magic
            numbers: `a'range` is `99 downto 0`, `a'high` is 99, `a'length` is 100.

            ```vhdl
            g: for i in din'range generate ... end generate g;
            ```
        """,
        verilog="Same as a 100-iteration `genvar` loop.",
        task="""
            Using the provided `full_adder`, generate a 100-bit ripple-carry adder and output
            every carry on `couts` (`couts(99)` is the final carry).
        """,
        ports="a, b: in slv(99:0); cin: in sl; sum: out slv(99:0); couts: out slv(99:0)",
        provided={"full_adder.vhd": FULL_ADDER},
        hints=["Exactly 4.8 with bigger numbers."],
    ),
    dict(
        num=12, name="bcd_ripple4",
        concept="generating a chain of a provided multi-bit cell.",
        intro="""
            BCD (binary-coded decimal) stores one decimal digit per 4-bit nibble, so
            `x"1234"` represents decimal 1234. A BCD adder adds digit by digit, passing a
            decimal carry from each digit to the next.

            Slices with computed bounds work in generate loops:
            `v(4*i + 3 downto 4*i)` is nibble `i`.
        """,
        verilog="Same as part-selects `v[4*i +: 4]` in a generate loop.",
        task="""
            The provided `bcd_fadd(a, b: in slv(3:0); cin: in sl; s: out slv(3:0); cout: out sl)`
            adds one BCD digit. Generate a 4-digit (16-bit) BCD adder. Inputs are always
            valid BCD.
        """,
        ports="a, b: in slv(15:0); cin: in sl; sum: out slv(15:0); cout: out sl",
        provided={"bcd_fadd.vhd": BCD_FADD},
        options={"nibble_range": {"a": [0, 9], "b": [0, 9]}},
        after_ports="The grader only generates valid BCD inputs (each nibble 0–9).",
        hints=["A 5-bit carry vector, nibble slices `4*i+3 downto 4*i`, and `cout` is the last carry."],
    ),
    dict(
        num=13, name="own_generic",
        concept="writing (not just using) a generic entity.",
        intro="""
            Your own entity can have generics. Inside the architecture, generics are constants,
            and port ranges can use them:

            ```vhdl
            entity pad is
              generic (W : positive := 8);
              port (din : in std_logic_vector(W - 1 downto 0); ...);
            ```

            Write the body without assuming any particular `W`: use `W` itself or attributes
            like `din'high`.
        """,
        verilog="`parameter W = 6` becomes `generic (W : positive := 6)`.",
        task="""
            The stub has `generic (W: positive := 6)`. Output `din` rotated left by one, for
            any `W`: the MSB wraps around to bit 0.

            The grader uses the default `W = 6`. Then try a different width:

            ```
            ./check.py 4.13 -g W=10
            ```
        """,
        ports="din: in slv(W-1:0); dout: out slv(W-1:0)",
        generics={"W": 6},
        hints=["`din(W - 2 downto 0) & din(W - 1)`"],
    ),
    dict(
        num=14, name="if_generate", mode="seq",
        concept="`if ... generate` controlled by a boolean generic.",
        intro="""
            `if ... generate` includes or excludes concurrent statements at elaboration time,
            based on a constant condition (usually a generic). VHDL-2008 allows `elsif` and
            `else` branches:

            ```vhdl
            g_dbg: if DEBUG generate
              led <= state_bits;
            else generate
              led <= (others => '0');
            end generate g_dbg;
            ```
        """,
        verilog="Same as a Verilog `generate if`.",
        task="""
            `generic (REGISTERED: boolean := true)`. When true, `y` is `a AND b` registered on
            the rising edge of `clk`; when false, it's `a AND b` combinationally. The grader
            checks the default, and `./check.py 4.14 -g REGISTERED=false` checks the other
            branch.
        """,
        ports="clk, a, b: in sl; y: out sl",
        generics={"REGISTERED": True},
        generic_types={"REGISTERED": "boolean"},
        hints=[
            "Two branches: one with a `process(clk)` and `if rising_edge(clk)`, one with a plain `y <= a and b;`.",
        ],
    ),
    dict(
        num=15, name="two_level_hier",
        concept="hierarchy deeper than one level; the learner writes a submodule entity in the same file.",
        intro="""
            A file can hold several design units. Each entity needs its own `library`/`use`
            context clause, because a context clause only applies to the next design unit.
            The sub-module has to come before the entity that instantiates it, since GHDL
            analyzes the file top to bottom.

            ```vhdl
            library ieee;
            use ieee.std_logic_1164.all;
            entity helper is ... end entity;
            architecture rtl of helper is ... end architecture;

            library ieee;
            use ieee.std_logic_1164.all;
            entity top_module is ...
            ```
        """,
        verilog="In Verilog, `module`s can appear in any order. VHDL needs the sub-module analyzed first.",
        task="""
            Write your own `entity sum3` (inputs `a, b, c`, output `y = a XOR b XOR c`) **in the
            same file**, above `top_module`. Instantiate it twice so that
            `y1 = sum3(a, b, c)` and `y2 = sum3(y1, d, e)`.
        """,
        ports="a, b, c, d, e: in sl; y1, y2: out sl",
        stub="""
            -- Write entity sum3 and its architecture here, with its own library/use clauses.


            library ieee;
            use ieee.std_logic_1164.all;

            entity top_module is
              port (
                a, b, c, d, e : in  std_logic;
                y1, y2        : out std_logic
              );
            end entity top_module;

            architecture rtl of top_module is
            begin
              -- Write your code here
            end architecture rtl;
        """,
        hints=[
            "`sum3` has ports like `a, b, c : in std_logic; y : out std_logic`.",
            "In VHDL-2008 you can connect the second instance directly to output port `y1`, since `out` ports are readable.",
        ],
    ),
]
