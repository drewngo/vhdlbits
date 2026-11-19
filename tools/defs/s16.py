SECTION = 16

HDR = "library ieee;\nuse ieee.std_logic_1164.all;\n"
NUM = HDR + "use ieee.numeric_std.all;\n"

INTRO = """
    This file is a complete design that compiles, but it has a bug. The task below says what
    the design is **supposed** to do. Find the bug with the grader and the waveform, and fix
    it, changing as little as possible.
"""

VERILOG = "Bugs like this one exist in Verilog too; the VHDL symptoms are what's worth learning to recognize."

PROBLEMS = [
    dict(
        num=1, name="bug_sensitivity", mode="stateful_comb",
        concept="debugging a combinational process.",
        intro=INTRO,
        verilog=VERILOG,
        task="A 3-input mux: `y = a` when `sel = \"00\"`, `b` when `sel = \"01\"`, and `c` otherwise.",
        ports="sel: in slv(1:0); a, b, c: in sl; y: out sl",
        stub=HDR + """
entity top_module is
  port (
    sel     : in  std_logic_vector(1 downto 0);
    a, b, c : in  std_logic;
    y       : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(sel, a, b)
  begin
    case sel is
      when "00"   => y <= a;
      when "01"   => y <= b;
      when others => y <= c;
    end case;
  end process;
end architecture rtl;
""",
        after_ports="The grader changes one input at a time and checks after each change.",
        hints=["When does this process run? Watch the waveform when only `c` changes."],
    ),
    dict(
        num=2, name="bug_latch",
        concept="debugging a combinational decoder.",
        intro=INTRO,
        verilog=VERILOG,
        task="""
            Decode a 4-bit opcode into control lines. Every output is `'0'` unless listed:

            | op | asserted outputs |
            |---|---|
            | `0001` | `alu_en` |
            | `0010` | `alu_en`, `wr_reg` |
            | `0100` | `mem_rd`, `wr_reg` |
            | `0101` | `mem_wr` |
            | `1000` | `branch` |
            | `1111` | `halt` |
            | anything else | none |
        """,
        ports="op: in slv(3:0); alu_en, wr_reg, mem_rd, mem_wr, branch, halt: out sl",
        stub=HDR + """
entity top_module is
  port (
    op                                           : in  std_logic_vector(3 downto 0);
    alu_en, wr_reg, mem_rd, mem_wr, branch, halt : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(all)
  begin
    case op is
      when "0001" => alu_en <= '1';
      when "0010" => alu_en <= '1'; wr_reg <= '1';
      when "0100" => mem_rd <= '1'; wr_reg <= '1';
      when "0101" => mem_wr <= '1';
      when "1000" => branch <= '1';
      when "1111" => halt   <= '1';
      when others => null;
    end case;
  end process;
end architecture rtl;
""",
        hints=["After `op = \"0001\"`, what is `alu_en` when `op` changes to `\"0000\"`?"],
    ),
    dict(
        num=3, name="bug_signal_vs_var", mode="seq",
        concept="debugging a clocked accumulator.",
        intro=INTRO,
        verilog=VERILOG,
        task="""
            A running total: at each rising edge, `total ← total + x` (12 bits, wrapping).
            `over` is registered and is `'1'` after an edge exactly when the **new** total is
            2048 or more. Active-high synchronous `reset` clears `total` and `over`.
        """,
        ports="clk, reset: in sl; x: in slv(7:0); total: out slv(11:0); over: out sl",
        options={"reset_prob": 0.02},
        stub=NUM + """
entity top_module is
  port (
    clk, reset : in  std_logic;
    x          : in  std_logic_vector(7 downto 0);
    total      : out std_logic_vector(11 downto 0);
    over       : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  signal acc : unsigned(11 downto 0);
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        acc  <= (others => '0');
        over <= '0';
      else
        acc <= acc + unsigned(x);
        if acc >= 2048 then
          over <= '1';
        else
          over <= '0';
        end if;
      end if;
    end if;
  end process;
  total <= std_logic_vector(acc);
end architecture rtl;
""",
        hints=["Which value of `acc` does the comparison see: before or after this edge's addition?"],
    ),
    dict(
        num=4, name="bug_numeric", numeric=True,
        concept="debugging a comparison.",
        intro=INTRO,
        verilog=VERILOG,
        task="`m` is the minimum of `a` and `b`, both 8-bit **signed** (two's complement).",
        ports="a, b: in slv(7:0); m: out slv(7:0)",
        stub=NUM + """
entity top_module is
  port (
    a, b : in  std_logic_vector(7 downto 0);
    m    : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  m <= a when unsigned(a) < unsigned(b) else b;
end architecture rtl;
""",
        hints=["Try `a = x\"FF\"` (−1) and `b = x\"01\"`."],
    ),
    dict(
        num=5, name="bug_resize", numeric=True,
        concept="debugging an adder.",
        intro=INTRO,
        verilog=VERILOG,
        task="`sum = a + b` for 8-bit unsigned inputs, as a full 9-bit result.",
        ports="a, b: in slv(7:0); sum: out slv(8:0)",
        stub=NUM + """
entity top_module is
  port (
    a, b : in  std_logic_vector(7 downto 0);
    sum  : out std_logic_vector(8 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  sum <= std_logic_vector(resize(unsigned(a) + unsigned(b), 9));
end architecture rtl;
""",
        hints=["How wide is `unsigned(a) + unsigned(b)`?"],
    ),
    dict(
        num=6, name="bug_off_by_one", mode="seq", numeric=True,
        concept="debugging a counter.",
        intro=INTRO,
        verilog=VERILOG,
        task="A decade counter `q`: 0–9, wrapping to 0. Active-high synchronous `reset` to 0.",
        ports="clk, reset: in sl; q: out slv(3:0)",
        stub=NUM + """
entity top_module is
  port (
    clk, reset : in  std_logic;
    q          : out std_logic_vector(3 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  signal cnt : unsigned(3 downto 0);
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' or cnt = 10 then
        cnt <= (others => '0');
      else
        cnt <= cnt + 1;
      end if;
    end if;
  end process;
  q <= std_logic_vector(cnt);
end architecture rtl;
""",
        hints=["List the values `q` takes after a reset."],
    ),
    dict(
        num=7, name="bug_async_reset", mode="seq",
        concept="debugging a register with reset.",
        intro=INTRO,
        verilog=VERILOG,
        task="8 flip-flops `q` loading `d` at each rising edge, with an active-high **asynchronous** reset `areset` to `x\"00\"`.",
        ports="clk, areset: in sl; d: in slv(7:0); q: out slv(7:0)",
        stub=HDR + """
entity top_module is
  port (
    clk, areset : in  std_logic;
    d           : in  std_logic_vector(7 downto 0);
    q           : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(clk, areset)
  begin
    if rising_edge(clk) then
      if areset = '1' then
        q <= x"00";
      else
        q <= d;
      end if;
    end if;
  end process;
end architecture rtl;
""",
        hints=["`areset` is in the sensitivity list, but what does the process do when it wakes up because of `areset` alone?"],
    ),
    dict(
        num=8, name="bug_fsm_default", mode="seq",
        concept="debugging a two-process FSM.",
        intro=INTRO,
        verilog=VERILOG,
        task="""
            `din` is sampled at each rising edge. `found` is `'1'` during the cycle after the
            edge at which the last four samples were `1, 0, 1, 1` (oldest first); overlapping
            matches count. Active-high synchronous `reset` forgets everything received so far.
        """,
        ports="clk, reset, din: in sl; found: out sl",
        stub=HDR + """
entity top_module is
  port (
    clk, reset, din : in  std_logic;
    found           : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  type state_t is (S_NONE, S_1, S_10, S_101, S_1011);
  signal state, next_state : state_t;
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        state <= S_NONE;
      else
        state <= next_state;
      end if;
    end if;
  end process;

  process(all)
  begin
    case state is
      when S_NONE =>
        if din = '1' then next_state <= S_1; end if;
      when S_1 =>
        if din = '0' then next_state <= S_10; end if;
      when S_10 =>
        if din = '1' then next_state <= S_101; else next_state <= S_NONE; end if;
      when S_101 =>
        if din = '1' then next_state <= S_1011; else next_state <= S_10; end if;
      when S_1011 =>
        if din = '1' then next_state <= S_1; else next_state <= S_10; end if;
    end case;
  end process;

  found <= '1' when state = S_1011 else '0';
end architecture rtl;
""",
        hints=["In `S_NONE` with `din = '0'`, what does `next_state` become?"],
    ),
    dict(
        num=9, name="bug_multiple_drivers", mode="seq",
        concept="debugging a register with two controls.",
        intro=INTRO,
        verilog=VERILOG,
        task="""
            An 8-bit register `q`. At each rising edge: if `clear = '1'`, `q` becomes 0;
            otherwise if `load = '1'`, `q` takes `d`; otherwise it holds. (`clear` has
            priority.)
        """,
        ports="clk, clear, load: in sl; d: in slv(7:0); q: out slv(7:0)",
        options={"bias": {"clear": 0.1, "load": 0.4}, "init": {"values": {"clear": 1}}},
        after_ports="The grader asserts `clear` in the first cycle so the register starts known.",
        stub=HDR + """
entity top_module is
  port (
    clk, clear, load : in  std_logic;
    d                : in  std_logic_vector(7 downto 0);
    q                : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  load_p: process(clk)
  begin
    if rising_edge(clk) then
      if load = '1' then
        q <= d;
      end if;
    end if;
  end process load_p;

  clear_p: process(clk)
  begin
    if rising_edge(clk) then
      if clear = '1' then
        q <= (others => '0');
      end if;
    end if;
  end process clear_p;
end architecture rtl;
""",
        hints=["Look for `'X'` in the waveform. Every process that assigns a signal is a driver of it."],
    ),
    dict(
        num=10, name="bug_integer_overflow", numeric=True,
        concept="debugging a counting loop.",
        intro=INTRO,
        verilog=VERILOG,
        task="`count` is the number of `'1'` bits in the 32-bit `din` (0–32).",
        ports="din: in slv(31:0); count: out slv(5:0)",
        options={"value_bias": {"din": [["FFFFFFFF", 0.02]]}},
        stub=NUM + """
entity top_module is
  port (
    din   : in  std_logic_vector(31 downto 0);
    count : out std_logic_vector(5 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(all)
    variable n : integer range 0 to 31;
  begin
    n := 0;
    for i in din'range loop
      if din(i) = '1' then
        n := n + 1;
      end if;
    end loop;
    count <= std_logic_vector(to_unsigned(n, 6));
  end process;
end architecture rtl;
""",
        hints=["Read GHDL's runtime error message carefully: which value didn't fit?"],
    ),
    dict(
        num=11, name="bug_shift", numeric=True,
        concept="debugging a shift.",
        intro=INTRO,
        verilog=VERILOG,
        task="`y = x / 4` for the 8-bit signed `x`, rounding toward −∞ (an arithmetic shift right by 2).",
        ports="x: in slv(7:0); y: out slv(7:0)",
        stub=NUM + """
entity top_module is
  port (
    x : in  std_logic_vector(7 downto 0);
    y : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  y <= x sll 2;
end architecture rtl;
""",
        hints=["Two things are wrong with that one operator: the direction, and what fills the vacated bits."],
    ),
    dict(
        num=12, name="bug_handshake", mode="seq",
        concept="debugging a valid/ready buffer.",
        intro=INTRO,
        verilog=VERILOG,
        task="""
            One-entry valid/ready buffer (as in 11.8):

            - `out_valid = '1'` whenever the buffer holds an entry, shown on `out_data`
            - `in_ready = '1'` when the buffer is empty **or** `out_ready = '1'`
            - at a rising edge, the entry leaves if `out_valid` and `out_ready` are `'1'`, and
              `in_data` is stored if `in_valid` and `in_ready` are `'1'` (both may happen)
            - `out_data` keeps the last stored value while empty

            Active-high synchronous `reset` → empty, `out_data = x"00"`.
        """,
        ports="clk, reset, in_valid, out_ready: in sl; in_data: in slv(7:0); in_ready, out_valid: out sl; out_data: out slv(7:0)",
        options={"bias": {"in_valid": 0.6, "out_ready": 0.5}, "reset_prob": 0.01},
        stub=HDR + """
entity top_module is
  port (
    clk, reset, in_valid, out_ready : in  std_logic;
    in_data                         : in  std_logic_vector(7 downto 0);
    in_ready, out_valid             : out std_logic;
    out_data                        : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  signal full  : std_logic;
  signal ready : std_logic;
  signal store : std_logic_vector(7 downto 0);
begin
  ready <= not full;

  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        full  <= '0';
        store <= x"00";
      else
        if full = '1' and out_ready = '1' then
          full <= '0';
        end if;
        if in_valid = '1' and ready = '1' then
          full  <= '1';
          store <= in_data;
        end if;
      end if;
    end if;
  end process;

  in_ready  <= ready;
  out_valid <= full;
  out_data  <= store;
end architecture rtl;
""",
        hints=["With a consumer that is always ready, how many cycles does each byte take?"],
    ),
    dict(
        num=13, name="bug_gray_loop",
        concept="debugging a loop.",
        intro=INTRO,
        verilog=VERILOG,
        task="Gray code to binary: `b(7) = g(7)`, and `b(i) = b(i+1) XOR g(i)` for lower bits.",
        ports="g: in slv(7:0); b: out slv(7:0)",
        stub=HDR + """
entity top_module is
  port (
    g : in  std_logic_vector(7 downto 0);
    b : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(all)
    variable acc : std_logic;
  begin
    acc := '0';
    for i in 0 to 7 loop
      acc  := acc xor g(i);
      b(i) <= acc;
    end loop;
  end process;
end architecture rtl;
""",
        hints=["Which bit should the running XOR start from?"],
    ),
    dict(
        num=14, name="bug_case_others",
        concept="debugging a mux.",
        intro=INTRO,
        verilog=VERILOG,
        task="A 6-to-1 mux of 4-bit inputs: `sel` 0–5 selects `d0`–`d5`; `sel` 6 or 7 outputs `\"0000\"`. (There are two bugs in this one.)",
        ports="sel: in slv(2:0); d0, d1, d2, d3, d4, d5: in slv(3:0); y: out slv(3:0)",
        stub=HDR + """
entity top_module is
  port (
    sel                    : in  std_logic_vector(2 downto 0);
    d0, d1, d2, d3, d4, d5 : in  std_logic_vector(3 downto 0);
    y                      : out std_logic_vector(3 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(all)
  begin
    case sel is
      when "000"  => y <= d0;
      when "001"  => y <= d1;
      when "010"  => y <= d2;
      when "011"  => y <= d3;
      when "100"  => y <= d5;
      when "101"  => y <= d5;
      when others => null;
    end case;
  end process;
end architecture rtl;
""",
        hints=["Read every choice against the task. Then ask what `y` is when `sel = \"110\"`."],
    ),
]
