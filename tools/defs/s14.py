import random
import textwrap

SECTION = 14

HDR = "library ieee;\nuse ieee.std_logic_1164.all;\n"
NUM = HDR + "use ieee.numeric_std.all;\n"


def _src(header, body):
    return header + textwrap.dedent(body)


def monitor(names):
    """A grader-side monitor that logs every change of its std_logic inputs to trace.txt."""
    ports = ", ".join(names)
    writes = "\n".join(f'      write(l, string\'(" {n}=") & to_string({n}));' for n in names)
    return HDR + "use std.textio.all;\n\n" + f"""-- Provided: do not edit. Logs every change of its inputs to trace.txt for the grader.
entity monitor is
  port ({ports} : in std_logic);
end entity monitor;

architecture sim of monitor is
begin
  process
    file f : text open write_mode is "trace.txt";
    variable l : line;
  begin
    loop
      write(l, integer(now / 1 ps));
{writes}
      writeline(f, l);
      wait on {ports};
    end loop;
  end process;
end architecture sim;
"""


STUB_TB = HDR + """
entity tb is
end entity tb;

architecture sim of tb is
begin
  -- Write your testbench here. End the simulation with std.env.finish.
end architecture sim;
"""

TRACE_NOTE = textwrap.indent(textwrap.dedent("""
    **How this is graded:** the grader runs your `tb` with the provided `monitor`, which
    logs every change of its inputs, and compares the log against the reference
    testbench's log. Only the final value at each instant counts, so it doesn't matter
    how many delta cycles your assignments take. Your simulation must end at the same
    time via `std.env.finish`.
"""), " " * 12)

MUTANT_NOTE = textwrap.indent(textwrap.dedent("""
    **How this is graded:** the grader runs your `tb` once with the correct design, where
    it must not report any `error` or `failure`, and once with each of several buggy
    *mutants* of the design, where it must report at least one. Mutants your testbench
    doesn't catch are listed as SURVIVED.
"""), " " * 12)

# ---- 14.3 -----------------------------------------------------------------
AND2 = HDR + """
-- Provided: do not edit.
entity and2 is
  port (
    a, b : in  std_logic;
    y    : out std_logic
  );
end entity and2;

architecture rtl of and2 is
begin
  y <= a and b;
end architecture rtl;
"""

# ---- 14.4 -----------------------------------------------------------------
MUX2_ENTITY = """
entity mux2 is
  port (
    a, b, sel : in  std_logic;
    y         : out std_logic
  );
end entity mux2;
"""


def mux2(body, note="-- Provided: do not edit. y = b when sel = '1', else a."):
    return HDR + "\n" + note + MUX2_ENTITY + f"""
architecture rtl of mux2 is
begin
  {body}
end architecture rtl;
"""


# ---- 14.5 -----------------------------------------------------------------
def decade(body):
    return NUM + """
entity decade is
  port (
    clk, reset : in  std_logic;
    q          : out std_logic_vector(3 downto 0)
  );
end entity decade;

architecture rtl of decade is
  signal cnt : unsigned(3 downto 0);
begin
""" + textwrap.indent(textwrap.dedent(body).strip("\n"), "  ") + """
  q <= std_logic_vector(cnt);
end architecture rtl;
"""


DECADE_OK = """
    -- Provided: do not edit. Counts 0..9 and wraps; active-high synchronous reset.
    process(clk)
    begin
      if rising_edge(clk) then
        if reset = '1' or cnt = 9 then
          cnt <= (others => '0');
        else
          cnt <= cnt + 1;
        end if;
      end if;
    end process;
"""

# ---- 14.6 -----------------------------------------------------------------
def adder8(body):
    return NUM + """
entity adder8 is
  port (
    a, b : in  std_logic_vector(7 downto 0);
    sum  : out std_logic_vector(8 downto 0)
  );
end entity adder8;

architecture rtl of adder8 is
begin
""" + textwrap.indent(textwrap.dedent(body).strip("\n"), "  ") + """
end architecture rtl;
"""


def _vectors():
    rng = random.Random(14)
    pairs = [(0x08, 0x08), (0x3C, 0x0F), (0xFF, 0x01), (0x80, 0x80), (0x10, 0xFF), (0x00, 0xFF), (0xFF, 0xFF)]
    pairs += [(rng.getrandbits(8), rng.getrandbits(8)) for _ in range(33)]
    return "".join(f"{a:02X} {b:02X} {a + b:03X}\n" for a, b in pairs)


VECTORS = _vectors()

# ---- 14.7 -----------------------------------------------------------------
def cmp16(expr):
    return NUM + """
entity cmp16 is
  port (
    a, b : in  std_logic_vector(15 downto 0);
    lt   : out std_logic
  );
end entity cmp16;

architecture rtl of cmp16 is
begin
  lt <= '1' when """ + expr + """ else '0';
end architecture rtl;
"""


# ---- 14.8 -----------------------------------------------------------------
def skid(ready_expr, drain_stmt):
    return HDR + f"""
entity skid1 is
  port (
    clk, reset, in_valid, out_ready : in  std_logic;
    in_data                         : in  std_logic_vector(7 downto 0);
    in_ready, out_valid             : out std_logic;
    out_data                        : out std_logic_vector(7 downto 0)
  );
end entity skid1;

architecture rtl of skid1 is
  signal full  : std_logic;
  signal ready : std_logic;
  signal store : std_logic_vector(7 downto 0);
begin
  ready <= {ready_expr};

  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        full  <= '0';
        store <= x"00";
      else
        if full = '1' and out_ready = '1' then
          {drain_stmt}
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
"""


PROBLEMS = [
    dict(
        num=1, name="clock_gen", mode="tb",
        concept="a clock process with `wait for`.",
        intro="""
            A testbench is an entity with no ports. Inside it, simulation-only constructs are
            fine: `wait for` delays, `after` clauses, file I/O.

            Two common ways to make a clock:

            ```vhdl
            sys_clk <= not sys_clk after 4 ns;          -- needs an initial value on the signal

            process
            begin
              sys_clk <= '0'; wait for 4 ns;
              sys_clk <= '1'; wait for 4 ns;
            end process;
            ```

            A testbench ends with `std.env.finish` (VHDL-2008) in some process; otherwise a
            free-running clock keeps the simulation going forever.
        """ + TRACE_NOTE,
        verilog="`always #5 clk = ~clk;` becomes `clk <= not clk after 5 ns;`, and `$finish` becomes `std.env.finish`.",
        task="""
            Write entity `tb` that generates `clk` with a 10 ns period, starting at `'0'` at
            time 0 (so it rises at 5 ns, 15 ns, …). Connect it to the monitor and end the
            simulation at 100 ns with `std.env.finish`.
        """,
        interfaces="""
            ```vhdl
            entity monitor is
              port (clk : in std_logic);
            end entity monitor;
            ```

            Instantiate it with `mon: entity work.monitor port map (clk => clk);`.
        """,
        stub=STUB_TB,
        provided={"monitor.vhd": monitor(["clk"])},
        options={"tb_kind": "trace"},
        hints=[
            "Declare `signal clk : std_logic := '0';`.",
            "A separate process: `wait for 100 ns; std.env.finish;`.",
        ],
    ),
    dict(
        num=2, name="stimulus_timeline", mode="tb",
        concept="a sequential stimulus process.",
        intro="""
            A stimulus process is a script: assign, wait, assign, wait. Each `wait for` is
            relative to the current time.

            ```vhdl
            process
            begin
              start <= '0';
              wait for 20 ns;
              start <= '1';
              wait for 10 ns;
              start <= '0';
              wait;                      -- a bare wait suspends forever
            end process;
            ```
        """ + TRACE_NOTE,
        verilog="An `initial` block with `#` delays. Note that `wait for 10 ns` is relative, like `#10`.",
        task="""
            Drive `a` and `b` (connected to the monitor) through this timeline, then call
            `std.env.finish` at 50 ns:

            | time | change |
            |---|---|
            | 0 ns | `a = '0'`, `b = '0'` |
            | 10 ns | `a = '1'` |
            | 20 ns | `b = '1'` |
            | 25 ns | `a = '0'` |
            | 40 ns | `b = '0'` |
            | 50 ns | end |
        """,
        interfaces="""
            ```vhdl
            entity monitor is
              port (a, b : in std_logic);
            end entity monitor;
            ```
        """,
        stub=STUB_TB,
        provided={"monitor.vhd": monitor(["a", "b"])},
        options={"tb_kind": "trace"},
        hints=["Waits are relative: from 20 ns to 25 ns is `wait for 5 ns`."],
    ),
    dict(
        num=3, name="tb_instance", mode="tb",
        concept="instantiating a DUT and driving it from a clock.",
        intro="""
            A typical testbench instantiates the design under test (DUT), generates a clock,
            and changes inputs on the falling edge so they're stable at the rising edge.
            `wait until falling_edge(clk);` synchronizes a stimulus process to the clock.
        """ + TRACE_NOTE,
        verilog="`@(negedge clk)` becomes `wait until falling_edge(clk);`.",
        task="""
            Instantiate the provided `and2` and the monitor. Generate `clk` with a 10 ns period
            starting at `'0'` (first falling edge at 10 ns). `a` and `b` start at `'0'`. On
            each of the first four falling edges drive `ab` = `00`, `01`, `10`, `11` (that is,
            `a = '0', b = '1'` on the second edge, and so on). Call `std.env.finish` at the
            fifth falling edge (50 ns). Connect `a`, `b` and the AND output `y` to the
            monitor (not the clock).
        """,
        interfaces="""
            ```vhdl
            entity and2 is
              port (a, b : in std_logic; y : out std_logic);
            end entity and2;

            entity monitor is
              port (a, b, y : in std_logic);
            end entity monitor;
            ```
        """,
        stub=STUB_TB,
        provided={"and2.vhd": AND2, "monitor.vhd": monitor(["a", "b", "y"])},
        options={"tb_kind": "trace"},
        hints=["A loop over the four values, each preceded by `wait until falling_edge(clk);`."],
    ),
    dict(
        num=4, name="assert_basics", mode="tb",
        concept="`assert cond report \"msg\" severity error`.",
        intro="""
            A self-checking testbench compares the DUT against the expected value and
            complains when they differ:

            ```vhdl
            assert parity_out = expected
              report "parity wrong for " & to_string(din)
              severity error;
            ```

            `severity error` prints the message and continues; `severity failure` stops the
            simulation. Remember the assertion fires when the condition is **false**.

            To test all inputs of a small combinational block, loop over every combination
            and wait a little after each so the outputs settle:

            ```vhdl
            for i in 0 to 7 loop
              vec <= std_logic_vector(to_unsigned(i, 3));
              wait for 1 ns;
              ...
            end loop;
            ```
        """ + MUTANT_NOTE,
        verilog="SystemVerilog `assert (cond) else $error(\"msg\");` is the closest equivalent.",
        task="Write an exhaustive self-checking testbench for the provided `mux2` (`y = b` when `sel = '1'`, else `a`). Check all 8 input combinations.",
        interfaces="""
            ```vhdl
            entity mux2 is
              port (a, b, sel : in std_logic; y : out std_logic);
            end entity mux2;
            ```

            There are 3 mutants.
        """,
        stub=STUB_TB,
        provided={"mux2.vhd": mux2("y <= b when sel = '1' else a;")},
        mutants={
            "inverted_sel.vhd": mux2("y <= a when sel = '1' else b;", "-- Mutant: select inverted."),
            "stuck_at_a.vhd": mux2("y <= a;", "-- Mutant: output always a."),
            "corner_case.vhd": mux2("y <= a when sel = '1' and a = '1' else b when sel = '1' else a;",
                                    "-- Mutant: wrong only for a=1, b=0, sel=1."),
        },
        options={"tb_kind": "mutant", "dut_file": "mux2.vhd"},
        hints=["Loop `i` over 0–7, split it into `a`, `b`, `sel`, wait 1 ns, and assert."],
    ),
    dict(
        num=5, name="tb_counter", mode="tb", numeric=True,
        concept="a clocked self-checking testbench with a reference model in the testbench.",
        intro="""
            For sequential designs, keep a **reference model** in the testbench: a variable
            that you update exactly as the DUT should, and compare after each clock edge.
            Check outputs away from the clock edges (e.g. just before the next rising edge),
            when they're stable.

            Don't only test the happy path: assert reset at different times, hold it for
            several cycles, run long enough to wrap.
        """ + MUTANT_NOTE,
        verilog="Same idea as a scoreboard in a Verilog testbench.",
        task="""
            Test the provided `decade` counter: it counts 0–9 and wraps, with an active-high
            **synchronous** `reset` to 0. Your testbench must catch all mutants, including one
            whose reset acts asynchronously.
        """,
        interfaces="""
            ```vhdl
            entity decade is
              port (clk, reset : in std_logic; q : out std_logic_vector(3 downto 0));
            end entity decade;
            ```

            There are 4 mutants.
        """,
        stub=STUB_TB,
        provided={"decade.vhd": decade(DECADE_OK)},
        mutants={
            "wraps_at_10.vhd": decade(DECADE_OK.replace("cnt = 9", "cnt = 10").replace(
                "Provided: do not edit. Counts 0..9 and wraps", "Mutant: counts 0..10")),
            "ignores_reset.vhd": decade(DECADE_OK.replace("reset = '1' or cnt = 9", "cnt = 9").replace(
                "Provided: do not edit.", "Mutant: reset ignored.")),
            "async_reset.vhd": decade("""
                -- Mutant: asynchronous reset.
                process(clk, reset)
                begin
                  if reset = '1' then
                    cnt <= (others => '0');
                  elsif rising_edge(clk) then
                    if cnt = 9 then
                      cnt <= (others => '0');
                    else
                      cnt <= cnt + 1;
                    end if;
                  end if;
                end process;
            """),
            "skips_after_5.vhd": decade("""
                -- Mutant: counts by 2 from 5 upward (5, 7, 9, 0).
                process(clk)
                begin
                  if rising_edge(clk) then
                    if reset = '1' or cnt >= 9 then
                      cnt <= (others => '0');
                    elsif cnt >= 5 then
                      cnt <= cnt + 2;
                    else
                      cnt <= cnt + 1;
                    end if;
                  end if;
                end process;
            """),
        },
        options={"tb_kind": "mutant", "dut_file": "decade.vhd"},
        hints=[
            "Start with reset high for a couple of cycles: `q` is `'U'` until the first reset edge.",
            "To catch the async mutant, change `reset` in the middle of a cycle and check `q` hasn't changed yet.",
        ],
    ),
    dict(
        num=6, name="tb_textio", mode="tb", numeric=True,
        concept="`std.textio` / `ieee.std_logic_textio`, reading vectors from a file.",
        intro="""
            Test vectors often come from a file produced by a reference model. `std.textio`
            reads text line by line: `readline` fetches a line, then `read`/`hread` parse
            values from it. In VHDL-2008, `hread` and `read` for `std_logic_vector` are part
            of `ieee.std_logic_1164`, so no extra package is needed.

            ```vhdl
            use std.textio.all;
            ...
            process
              file vec_file : text open read_mode is "golden.txt";
              variable l    : line;
              variable x    : std_logic_vector(15 downto 0);
            begin
              while not endfile(vec_file) loop
                readline(vec_file, l);
                hread(l, x);
                ...
              end loop;
              std.env.finish;
            end process;
            ```
        """ + MUTANT_NOTE,
        verilog="`$readmemh` / `$fscanf` become `textio` calls.",
        task="""
            The provided `vectors.txt` (copied next to your testbench when it runs) has one
            test per line: `a b expected_sum` in hex, for example `3C 0F 04B`. Read every
            line, apply it to the provided 8-bit adder, and assert that `sum` matches.
        """,
        interfaces="""
            ```vhdl
            entity adder8 is
              port (a, b : in std_logic_vector(7 downto 0); sum : out std_logic_vector(8 downto 0));
            end entity adder8;
            ```

            `vectors.txt` is in `provided/`. There are 3 mutants.
        """,
        stub=STUB_TB,
        provided={
            "adder8.vhd": adder8("-- Provided: do not edit.\nsum <= std_logic_vector(resize(unsigned(a), 9) + unsigned(b));"),
            "vectors.txt": VECTORS,
        },
        mutants={
            "carry_lost_bit4.vhd": adder8("""
                -- Mutant: no carry from bit 3 into bit 4.
                sum(3 downto 0) <= std_logic_vector(unsigned(a(3 downto 0)) + unsigned(b(3 downto 0)));
                sum(8 downto 4) <= std_logic_vector(resize(unsigned(a(7 downto 4)), 5) + unsigned(b(7 downto 4)));
            """),
            "no_carry_out.vhd": adder8("""
                -- Mutant: wraps at 8 bits, sum(8) always '0'.
                sum <= '0' & std_logic_vector(unsigned(a) + unsigned(b));
            """),
            "subtracts_ff.vhd": adder8("""
                -- Mutant: subtracts when b = x"FF".
                sum <= std_logic_vector(resize(unsigned(a), 9) - unsigned(b)) when b = x"FF"
                       else std_logic_vector(resize(unsigned(a), 9) + unsigned(b));
            """),
        },
        options={"tb_kind": "mutant", "dut_file": "adder8.vhd", "data_files": ["vectors.txt"]},
        hints=[
            "`hread(l, v)` works for a 9-bit vector too: it reads 3 hex digits, and the unused top bits must be 0.",
            "Wait 1 ns after applying each vector before checking.",
        ],
    ),
    dict(
        num=7, name="tb_random", mode="tb", numeric=True,
        concept="`ieee.math_real.uniform` for constrained-random stimulus.",
        intro="""
            `ieee.math_real` provides `uniform(seed1, seed2, x)`, which returns a real `x` in
            (0, 1) and updates the two seed variables. Scale it to get integers:

            ```vhdl
            use ieee.math_real.all;
            ...
            variable s1, s2 : positive := 42;
            variable r      : real;
            ...
            uniform(s1, s2, r);
            v := to_signed(integer(floor(r * 256.0)) - 128, 8);     -- -128 .. 127
            ```

            Random tests find the bugs you didn't think of; a reference model computes the
            expected result for whatever came out.
        """ + MUTANT_NOTE,
        verilog="`$random` / `$urandom` become `uniform` with explicit seed variables.",
        task="Test the provided 16-bit signed comparator (`lt = '1'` when `a < b` as signed) with 1000 random vectors, checking each against `signed(a) < signed(b)` computed in the testbench.",
        interfaces="""
            ```vhdl
            entity cmp16 is
              port (a, b : in std_logic_vector(15 downto 0); lt : out std_logic);
            end entity cmp16;
            ```

            There are 3 mutants, each wrong only around the sign bit.
        """,
        stub=STUB_TB,
        provided={"cmp16.vhd": cmp16("signed(a) < signed(b)")},
        mutants={
            "unsigned.vhd": cmp16("unsigned(a) < unsigned(b)"),
            "both_negative.vhd": cmp16("(signed(a) < signed(b)) xor (a(15) = '1' and b(15) = '1')"),
            "ignores_bit14.vhd": cmp16("signed(a(15) & a(13 downto 0)) < signed(b(15) & b(13 downto 0))"),
        },
        options={"tb_kind": "mutant", "dut_file": "cmp16.vhd"},
        hints=["`integer(floor(r * 65536.0))` gives 0–65535; convert with `to_unsigned(..., 16)`."],
    ),
    dict(
        num=8, name="tb_handshake", mode="tb", numeric=True,
        concept="testbench procedures for bus transactions.",
        intro="""
            Bus-level testbenches wrap the signal wiggling in procedures, so the test reads as
            transactions. A procedure declared in a process can drive that process's signals
            and wait:

            ```vhdl
            procedure write_reg(addr : natural; val : std_logic_vector(7 downto 0)) is
            begin
              wr_addr <= std_logic_vector(to_unsigned(addr, 4));
              wr_data <= val;
              wr_en   <= '1';
              wait until rising_edge(clk);
              wr_en   <= '0';
            end procedure;
            ```

            For a valid/ready interface, a sender holds `valid` and the data until it sees
            `ready` at a rising edge, and a receiver checks data only on edges where both
            `valid` and `ready` are high. Randomizing `ready` (backpressure) exposes bugs that
            a always-ready consumer never sees.
        """ + MUTANT_NOTE,
        verilog="Same as Verilog `task`s that wait on clock edges.",
        task="""
            Test the provided one-entry buffer `skid1` (the 11.8 design) with a
            `procedure send(byte)` in a producer process and a `procedure expect(byte)` in a
            consumer process that randomizes `out_ready`. Send at least 50 bytes and check
            that every byte comes out exactly once, in order. Also check the handshake rule
            from 11.8: `in_ready` must be `'1'` whenever the buffer is empty
            (`out_valid = '0'`).
        """,
        interfaces="""
            ```vhdl
            entity skid1 is
              port (
                clk, reset, in_valid, out_ready : in  std_logic;
                in_data                         : in  std_logic_vector(7 downto 0);
                in_ready, out_valid             : out std_logic;
                out_data                        : out std_logic_vector(7 downto 0)
              );
            end entity skid1;
            ```

            There are 3 mutants.
        """,
        stub=STUB_TB,
        provided={"skid1.vhd": skid("(not full) or out_ready", "full <= '0';")},
        mutants={
            "drops_data.vhd": skid("'1'", "full <= '0';"),
            "duplicates.vhd": skid("(not full) or out_ready", "null;"),
            "not_ready_when_empty.vhd": skid("out_ready", "full <= '0';"),
        },
        options={"tb_kind": "mutant", "dut_file": "skid1.vhd", "stop_time": "100us"},
        hints=[
            "Drive inputs a little after the rising edge (or on the falling edge) and sample on the rising edge.",
            "Give the consumer a timeout so a stuck design ends with an error instead of running until the stop time.",
        ],
    ),
]
