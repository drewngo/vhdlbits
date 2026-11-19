SECTION = 8

PROBLEMS = [
    dict(
        num=1, name="dff", mode="seq",
        concept="the D flip-flop.",
        intro="""
            The canonical register: a process sensitive to the clock, with everything inside
            `if rising_edge(clk)`.

            ```vhdl
            process(clk)
            begin
              if rising_edge(clk) then
                held <= sample;
              end if;
            end process;
            ```

            `clk'event and clk = '1'` is an older spelling you'll see in legacy code;
            `rising_edge` is preferred because it ignores `'X'`→`'1'` and similar transitions.
        """,
        verilog="`always @(posedge clk) q <= d;`",
        task="A single D flip-flop: `q` takes the value of `d` at every rising edge of `clk`.",
        ports="clk, d: in sl; q: out sl",
        hints=["Five lines: `process(clk)`, `begin`, `if rising_edge(clk) then`, `q <= d;`, and the closing `end`s."],
    ),
    dict(
        num=2, name="dff8_sync_reset", mode="seq",
        concept="synchronous reset, checked inside `rising_edge`.",
        intro="""
            A **synchronous** reset only acts on a clock edge, so it goes *inside* the
            `rising_edge` test:

            ```vhdl
            if rising_edge(clk) then
              if clear = '1' then
                total <= (others => '0');
              else
                total <= next_total;
              end if;
            end if;
            ```

            The sensitivity list stays `process(clk)`: nothing happens between edges.
        """,
        verilog="`always @(posedge clk) if (reset) q <= 0; else q <= d;`",
        task="8 flip-flops with an active-high **synchronous** `reset` to `x\"00\"`.",
        ports="clk, reset: in sl; d: in slv(7:0); q: out slv(7:0)",
        hints=["Reset is checked inside `if rising_edge(clk)`."],
    ),
    dict(
        num=3, name="dff8_async_reset", mode="seq",
        concept="async reset in the sensitivity list, `if reset = '1' then ... elsif rising_edge(clk)`.",
        intro="""
            An **asynchronous** reset acts immediately, without waiting for a clock edge. It
            goes in the sensitivity list and is tested *before* the clock:

            ```vhdl
            process(clk, rst)
            begin
              if rst = '1' then
                state <= IDLE;
              elsif rising_edge(clk) then
                state <= next_state;
              end if;
            end process;
            ```

            The grader compares outputs in the middle of each cycle too, so a synchronous
            implementation fails here: its output only clears at the next edge.
        """,
        verilog="`always @(posedge clk or posedge areset)` becomes `process(clk, areset)` with the reset tested first.",
        task="Same as 8.2, but the active-high reset `areset` is **asynchronous**.",
        ports="clk, areset: in sl; d: in slv(7:0); q: out slv(7:0)",
        hints=["`if areset = '1' then ... elsif rising_edge(clk) then ... end if;`"],
    ),
    dict(
        num=4, name="dff_enable", mode="seq",
        concept="clock enable (not clock gating).",
        intro="""
            To make a register update only sometimes, use an **enable** inside the clocked
            process. Never gate the clock itself (`clk and en`): that creates glitches and
            timing problems in an FPGA.

            ```vhdl
            if rising_edge(clk) then
              if load = '1' then
                cfg <= cfg_in;
              end if;           -- otherwise cfg keeps its value: that's what a register does
            end if;
            ```

            A missing `else` in a *clocked* process is fine: it means "hold". (It's only a
            latch problem in combinational processes.)
        """,
        verilog="`if (en) q <= d;` inside `always @(posedge clk)`.",
        task="8-bit register with active-high synchronous `reset` to 0. Load `d` only when `en = '1'`. Reset has priority over the enable.",
        ports="clk, reset, en: in sl; d: in slv(7:0); q: out slv(7:0)",
        hints=["`if reset = '1' then ... elsif en = '1' then ... end if;` inside the clock edge."],
    ),
    dict(
        num=5, name="rise_detect", mode="seq",
        concept="remembering the previous input.",
        intro="""
            An edge detector compares the input with a registered copy of itself:

            ```vhdl
            if rising_edge(clk) then
              btn_d   <= btn;
              pressed <= btn and not btn_d;    -- btn_d is still last cycle's value here
            end if;
            ```

            Because `btn_d` is a signal, reading it in the same process gives the old value,
            which is exactly what an edge detector needs.
        """,
        verilog="Same as two nonblocking assignments in one `always @(posedge clk)`.",
        task="""
            For each of the 8 bits, `pulse(i)` is `'1'` for one cycle after the cycle in which
            `din(i)` went from 0 to 1. `pulse` is a registered output: at each rising edge it
            becomes `din and not (din at the previous edge)`.
        """,
        ports="clk: in sl; din: in slv(7:0); pulse: out slv(7:0)",
        hints=["Bitwise operators handle all 8 bits at once."],
    ),
    dict(
        num=6, name="any_edge", mode="seq",
        concept="detecting a change in either direction.",
        intro="""
            A change in either direction is the XOR of the current and previous values.
        """,
        verilog="`pulse <= din ^ prev;`",
        task="Same as 8.5, but `pulse(i)` flags both rising and falling edges of `din(i)`.",
        ports="clk: in sl; din: in slv(7:0); pulse: out slv(7:0)",
        hints=["Change one operator from 8.5."],
    ),
    dict(
        num=7, name="sticky_capture", mode="seq",
        concept="set-dominant registers.",
        intro="""
            A **sticky** bit sets on an event and stays set until something clears it, like an
            interrupt status register:

            ```vhdl
            if rising_edge(clk) then
              if clear = '1' then
                status <= (others => '0');
              else
                status <= status or events;
              end if;
            end if;
            ```
        """,
        verilog="Same pattern with `|`.",
        task="""
            `cap(i)` goes high at the rising edge where a **falling** edge of `din(i)` is seen
            (`din(i)` was `'1'` at the previous edge and is `'0'` now), and stays high until
            reset. `reset` is synchronous and active-high, and it wins over a capture in the
            same cycle.

            The register holding the previous value of `din` is updated on every edge and
            is **not** affected by `reset`.
        """,
        ports="clk, reset: in sl; din: in slv(31:0); cap: out slv(31:0)",
        hints=[
            "A falling edge is `prev and not din`.",
            "`cap <= cap or (prev and not din);` unless reset.",
        ],
    ),
    dict(
        num=8, name="dff_negedge", mode="seq",
        concept="`falling_edge(clk)`.",
        intro="""
            `falling_edge(clk)` works just like `rising_edge`. Designs that use both edges of
            one clock are rare in FPGAs. They halve the time available for logic between the
            two edges.
        """,
        verilog="`always @(negedge clk)`.",
        task="8-bit register with active-high synchronous `reset` to `x\"5A\"`, updating on the **falling** edge of `clk`.",
        ports="clk, reset: in sl; d: in slv(7:0); q: out slv(7:0)",
        options={"input_offset": 1},
        after_ports="The grader changes inputs 1 ns after each falling edge for this problem, so they are stable when your register samples them.",
        hints=["Replace `rising_edge` with `falling_edge` in 8.2."],
    ),
    dict(
        num=9, name="byte_enable_reg", mode="seq",
        concept="partial updates of a register; active-low reset.",
        intro="""
            Slices of a register can be updated independently: a slice assignment only
            changes those bits, and the rest hold.

            ```vhdl
            if wr_hi = '1' then word(15 downto 8) <= din(15 downto 8); end if;
            ```

            Active-low signals conventionally end in `_n` or `n`; test them against `'0'`.
        """,
        verilog="`if (!resetn)` becomes `if resetn = '0' then`.",
        task="""
            16-bit register `q`. `be(1)` enables writing the upper byte from `d(15 downto 8)`,
            and `be(0)` the lower byte from `d(7 downto 0)`. Synchronous **active-low** reset
            `resetn` clears `q` to 0.
        """,
        ports="clk, resetn: in sl; be: in slv(1:0); d: in slv(15:0); q: out slv(15:0)",
        hints=["Two independent `if`s inside the `else` branch of the reset."],
    ),
    dict(
        num=10, name="d_latch", mode="stateful_comb",
        concept="what a latch is and why you usually don't want one.",
        intro="""
            A **latch** is transparent while its enable is high and holds while it's low. In a
            process, it appears whenever an output isn't assigned on some path:

            ```vhdl
            process(all)
            begin
              if gate = '1' then
                held <= sample;     -- no else: held keeps its value when gate = '0'
              end if;
            end process;
            ```

            FPGA tools support latches but warn about them, because their timing is hard to
            analyse and they are usually a bug (see 5.6 and 16.2). Here, for once, it's the
            point.

            There's no clock in this problem. The grader changes one input at a time and
            compares after each change.
        """,
        verilog="Same as an incomplete `if` in `always @(*)`.",
        task="`q` follows `d` while `en = '1'` and holds its value while `en = '0'`.",
        ports="d, en: in sl; q: out sl",
        hints=["The process above, with your names."],
    ),
    dict(
        num=11, name="jk_ff", mode="seq",
        concept="a flip-flop with a feedback-dependent next state, and signal initial values.",
        intro="""
            A signal declaration can give an **initial value**:

            ```vhdl
            signal count : unsigned(3 downto 0) := (others => '0');
            ```

            In simulation it's the value at time 0. On most FPGAs (Xilinx, Intel, Lattice)
            synthesis also honors it as the power-up value of the register. ASICs ignore
            initial values, so ASIC designs always need a reset.

            Because an `out` port is readable in VHDL-2008, you *could* use `q` directly, but
            a port can't have its own initial value here, so the stub gives you an internal
            signal that starts at `'0'`.
        """,
        verilog="`reg q = 0;` is the same idea.",
        task="""
            JK flip-flop. At each rising edge:

            | j | k | next `q` |
            |---|---|---|
            | 0 | 0 | hold |
            | 0 | 1 | `'0'` |
            | 1 | 0 | `'1'` |
            | 1 | 1 | toggle |

            Use the internal signal `q_int` (initialized to `'0'`) as the state.
        """,
        ports="clk, j, k: in sl; q: out sl",
        arch_decls="signal q_int : std_logic := '0';",
        arch_body="""
            q <= q_int;

            -- Write your code here
        """,
        hints=["A `case` on `std_logic_vector'(j & k)` inside the clock edge."],
    ),
    dict(
        num=12, name="t_ff", mode="seq",
        concept="toggling from the current state.",
        intro="""
            A toggle flip-flop inverts its state when `t = '1'`. The next state depends on
            the current one, so the process reads back the signal it assigns. That's fine
            for a register: the read gives last cycle's value.
        """,
        verilog="`q <= q ^ t;`",
        task="Toggle flip-flop: at each rising edge, `q` inverts when `t = '1'` and holds otherwise. Active-high synchronous `reset` clears `q`.",
        ports="clk, reset, t: in sl; q: out sl",
        hints=["`q <= q xor t;` — VHDL-2008 lets you read the `out` port `q`."],
    ),
    dict(
        num=13, name="sync2", mode="seq",
        concept="a two-flop synchronizer for a signal from another clock domain.",
        intro="""
            A signal from another clock domain (or a button) can change right at your clock
            edge. The first flip-flop that samples it may go **metastable**: its output
            hovers between 0 and 1 for an unpredictable time before settling. A second
            flip-flop gives it a whole clock period to settle, making failures astronomically
            rare.

            Rules: only single-bit signals go through a plain synchronizer (multi-bit values
            need a handshake or a FIFO), and nothing else may read the first stage.
            Vendors also let you mark the pair (e.g. Xilinx `ASYNC_REG`) so placement keeps
            them close.

            In simulation, metastability doesn't exist. The grader only checks the two-cycle
            delay.
        """,
        verilog="Same two-flop chain.",
        task="Pass `async_in` through two flip-flops to `sync_out`.",
        ports="clk, async_in: in sl; sync_out: out sl",
        hints=["An internal signal for the first stage; both assignments in one clocked process."],
    ),
    dict(
        num=14, name="dual_edge", mode="seq",
        concept="FPGAs don't have dual-edge flip-flops, so you build the behavior from two.",
        intro="""
            `if rising_edge(clk) or falling_edge(clk)` simulates, but no FPGA flip-flop can
            implement it, and synthesis will reject it. The usual trick: one register on each
            edge, and a mux driven by the clock selects whichever was updated most recently.

            (Feeding a clock into logic is normally a bad idea; this is one of the few places
            you'll see it.)
        """,
        verilog="`always @(posedge clk or negedge clk)` is not synthesizable either.",
        task="`q` takes the value of `d` on **both** edges of `clk`.",
        ports="clk, d: in sl; q: out sl",
        options={"input_offset": 2.5},
        after_ports="For this problem the grader changes inputs 2.5 ns after each falling edge, away from both clock edges.",
        hints=[
            "One process on `rising_edge`, one on `falling_edge`, each with its own register.",
            "`q <= q_pos when clk = '1' else q_neg;`",
        ],
    ),
    dict(
        num=15, name="pipeline3", mode="seq", numeric=True,
        concept="pipeline registers and latency.",
        intro="""
            A pipeline splits a long combinational path with registers so the clock can run
            faster. Every value that travels alongside must be delayed by the same number of
            stages, or the stages will mix data from different cycles.

            ```vhdl
            if rising_edge(clk) then
              s1_sum <= x + z;      -- stage 1
              s1_k   <= k;          -- k travels with its sum
              s2_out <= s1_sum * s1_k;
            end if;
            ```
        """,
        verilog="Same idea; the multiplication width rules from 6.11 apply.",
        task="""
            Compute `y = (a + b) * c` (8-bit unsigned inputs, 17-bit result) with **exactly 2
            cycles** of latency: register after the add and after the multiply. An active-high
            synchronous `reset` clears every pipeline register to 0.
        """,
        ports="clk, reset: in sl; a, b, c: in slv(7:0); y: out slv(16:0)",
        hints=[
            "Stage 1: a 9-bit sum and a delayed copy of `c`. Stage 2: the 17-bit product.",
            "9 bits × 8 bits = 17 bits.",
        ],
    ),
]
