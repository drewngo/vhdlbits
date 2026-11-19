SECTION = 9

PROBLEMS = [
    dict(
        num=1, name="count16", mode="seq", numeric=True,
        concept="an `unsigned` counter signal, `+ 1`, wraparound.",
        intro="""
            Keep the count in an internal `unsigned` signal, add 1 each clock, and convert to
            `std_logic_vector` for the port. `unsigned` arithmetic wraps silently at its width:
            `"1111" + 1` is `"0000"`.

            ```vhdl
            signal ticks : unsigned(5 downto 0);
            ...
            ticks <= ticks + 1;           -- inside if rising_edge(clk)
            count_out <= std_logic_vector(ticks);
            ```
        """,
        verilog="`q <= q + 1;` works the same once `q` is `unsigned`; on a raw `std_logic_vector` there is no `+`.",
        task="A 4-bit counter `q` that counts 0–15 and wraps. Active-high synchronous `reset` to 0.",
        ports="clk, reset: in sl; q: out slv(3:0)",
        hints=["An `unsigned(3 downto 0)` signal, and `q <= std_logic_vector(cnt);` outside the process."],
    ),
    dict(
        num=2, name="decade", mode="seq", numeric=True,
        concept="wrapping at an arbitrary limit.",
        intro="""
            To wrap somewhere other than a power of two, compare before incrementing:

            ```vhdl
            if minute = 59 then minute <= (others => '0'); else minute <= minute + 1; end if;
            ```

            `unsigned = integer` comparisons are defined in `numeric_std`.
        """,
        verilog="Same comparison; no casting needed once the signal is `unsigned`.",
        task="A counter `q` that counts 0–9 and wraps. Active-high synchronous `reset` to 0.",
        ports="clk, reset: in sl; q: out slv(3:0)",
        hints=["`if cnt = 9 then cnt <= (others => '0'); else cnt <= cnt + 1; end if;`"],
    ),
    dict(
        num=3, name="count_en_tc", mode="seq", numeric=True,
        concept="enable + terminal-count output.",
        intro="""
            A **terminal count** output tells the next counter in a chain "I'm about to wrap".
            Qualifying it with the enable makes chains work: the next stage should only
            advance when this stage actually wraps.

            ```vhdl
            carry_out <= '1' when cnt = 15 and step = '1' else '0';
            ```

            That's a combinational output from the register and the current input.
        """,
        verilog="`assign tc = (q == 8'hFF) && en;`",
        task="""
            8-bit counter `q` with active-high synchronous `reset` and an enable `en`: it
            increments (wrapping 255 → 0) only on edges where `en = '1'`. `tc` is `'1'`
            combinationally when `q = 255` **and** `en = '1'`.
        """,
        ports="clk, reset, en: in sl; q: out slv(7:0); tc: out sl",
        options={"cycles": 1500, "reset_prob": 0.002, "bias": {"en": 0.9}},
        hints=["`tc` is a concurrent assignment outside the clocked process."],
    ),
    dict(
        num=4, name="tick_gen", mode="seq", numeric=True,
        concept="clock-enable pulse generation (the right way to get a slow clock).",
        intro="""
            To run part of a design slower, don't divide the clock: generate a one-cycle
            **enable pulse** at the slower rate and keep everything on the fast clock. That
            keeps the design in one clock domain.

            A free-running modulo-N counter gives one pulse per N cycles.
        """,
        verilog="Same technique. Avoid `always @(posedge slow_clk)` with a derived clock.",
        task="""
            `tick` is `'1'` for exactly one cycle out of every 5. Use a counter that resets to
            0 and counts 0, 1, 2, 3, 4, 0, …, and make `tick` `'1'` while the counter is 4.

            So after the reset edge, the counter is 0 during the first cycle and `tick` is
            high during the 5th cycle. `tick` depends only on the counter, not on any input.
            `reset` is active-high and synchronous.
        """,
        ports="clk, reset: in sl; tick: out sl",
        hints=["A `0 to 4` counter and `tick <= '1' when cnt = 4 else '0';`"],
    ),
    dict(
        num=5, name="bcd_counter2", mode="seq", numeric=True,
        concept="cascading counters with enables.",
        intro="""
            Counters chain by enables: the second stage advances when the first stage is
            about to wrap *and* is enabled. Everything stays on the same clock.
        """,
        verilog="Same structure: no ripple clocks.",
        task="""
            A two-digit BCD counter 00–99 that wraps to 00, with active-high synchronous
            `reset`. On each edge with `en = '1'`, `ones` increments (9 → 0); when `ones` rolls
            over from 9 to 0, `tens` increments as well (9 → 0). Nothing changes when
            `en = '0'`.
        """,
        ports="clk, reset, en: in sl; ones, tens: out slv(3:0)",
        options={"cycles": 600, "reset_prob": 0.004, "bias": {"en": 0.8}},
        hints=["`tens` advances when `en = '1'` and `ones = 9`."],
    ),
    dict(
        num=6, name="clock_hms", mode="seq", numeric=True,
        concept="chained counters with different moduli.",
        intro="""
            A clock is a chain of BCD counters with different wrap points: seconds and
            minutes wrap at 59, hours at 23. Each two-digit field is its own
            ones/tens pair, and the carries chain all the way up.

            Hours are the tricky field: the tens digit wraps at 2, but the ones digit then
            wraps at 3 instead of 9.
        """,
        verilog="Same structure.",
        task="""
            A 24-hour clock in BCD: `hh` 00–23, `mm` 00–59, `ss` 00–59, each as two BCD digits
            (`hh(7 downto 4)` is the tens digit). It advances one second on each edge where
            `en = '1'`; 23:59:59 rolls over to 00:00:00. Active-high synchronous `reset` to
            00:00:00.
        """,
        ports="clk, reset, en: in sl; hh, mm, ss: out slv(7:0)",
        options={"cycles": 100000, "reset_prob": 0, "bias": {"en": 0.9}},
        after_ports="The grader runs 100k cycles so that the hours roll over at least once.",
        hints=[
            "Write a small helper: a function that increments a BCD pair with a given maximum, or nest `if`s.",
            "Seconds wrap at x\"59\"; minutes advance only when seconds wrap; hours only when both do.",
        ],
    ),
    dict(
        num=7, name="count_1_to_12", mode="seq", numeric=True,
        concept="a counter that doesn't start at zero.",
        intro="""
            Not every counter starts at 0. The reset value and the wrap value are both just
            constants.
        """,
        verilog="Same.",
        task="A counter that counts 1, 2, …, 12, 1, … with active-high synchronous `reset` to 1.",
        ports="clk, reset: in sl; q: out slv(3:0)",
        hints=["Reset to 1, and wrap from 12 to 1."],
    ),
    dict(
        num=8, name="updown", mode="seq", numeric=True,
        concept="two directions of wraparound.",
        intro="""
            `unsigned` wraps both ways: `"00000000" - 1` is `"11111111"`.
        """,
        verilog="Same.",
        task="8-bit up/down counter `q`. When `en = '1'`, it counts up if `up = '1'` and down otherwise, wrapping both ways. Holds when `en = '0'`. Active-high synchronous `reset` to 0.",
        ports="clk, reset, en, up: in sl; q: out slv(7:0)",
        options={"bias": {"up": 0.3}},
        hints=["Nested `if`s: reset, then enable, then direction."],
    ),
    dict(
        num=9, name="countdown_timer", mode="seq", numeric=True,
        concept="load + count down + done flag.",
        intro="""
            A down-counter with a parallel load is the core of most timers: load the duration,
            count down, raise a flag at zero.
        """,
        verilog="Same.",
        task="""
            On an edge where `load = '1'`, `q` loads `d`. Otherwise it decrements while it is
            nonzero and stops at 0. `done` is `'1'` while `q` is 0 (it depends only on `q`).
            Active-high synchronous `reset` sets `q` to 0 and has priority over `load`.
        """,
        ports="clk, reset, load: in sl; d: in slv(7:0); q: out slv(7:0); done: out sl",
        options={"bias": {"load": 0.05}, "range": {"d": [0, 40]}},
        hints=["`elsif cnt /= 0 then cnt <= cnt - 1;`"],
    ),
    dict(
        num=10, name="decade_slowena", mode="seq", numeric=True,
        concept="a counter driven by a slow enable.",
        intro="""
            Combine 9.2 with an enable: this is the building block of every divider chain,
            driven by a tick like the one from 9.4.
        """,
        verilog="Same.",
        task="Decade counter `q` (0–9, wraps) that advances only on edges where `slowena = '1'`. Active-high synchronous `reset` to 0.",
        ports="clk, reset, slowena: in sl; q: out slv(3:0)",
        hints=["9.2 with the increment inside `if slowena = '1'`."],
    ),
    dict(
        num=11, name="div1000_enables", mode="seq", numeric=True,
        concept="building a divider from cascaded decade counters and exposing their enables.",
        intro="""
            Three decade counters in a chain divide by 1000. Stage 0 counts every cycle;
            stage 1 advances when stage 0 is at 9; stage 2 when both stage 0 and stage 1 are
            at 9. When all three are at 9, the next edge wraps them all, so that's when the
            1000-cycle tick fires.
        """,
        verilog="Same structure.",
        task="""
            Build three decade counters `c0`, `c1`, `c2` (each 0–9, all reset to 0 by the
            active-high synchronous `reset`).

            - `enables(0)` is always `'1'`: stage 0 counts every cycle.
            - `enables(1)` is `'1'` when `c0 = 9`.
            - `enables(2)` is `'1'` when `c0 = 9` and `c1 = 9`.
            - `tick` is `'1'` when all three counters are 9.

            Each stage increments (wrapping 9 → 0) on edges where its enable is `'1'`. The
            outputs are combinational from the counter values, so `tick` is high for one
            cycle in every 1000.
        """,
        ports="clk, reset: in sl; enables: out slv(2:0); tick: out sl",
        options={"cycles": 5000, "reset_prob": 0},
        hints=["One process with three counters, plus concurrent assignments for the enables."],
    ),
    dict(
        num=12, name="johnson4", mode="seq",
        concept="a twisted-ring counter.",
        intro="""
            A **Johnson counter** is a shift register whose input is the inverted last bit.
            An n-bit Johnson counter cycles through 2n states, and every step changes exactly
            one bit, so decoding any state needs only a 2-input gate.
        """,
        verilog="`q <= {q[2:0], ~q[3]};`",
        task="""
            4-bit Johnson counter: at each edge, `q` shifts left by one and the inverse of the
            old `q(3)` enters at `q(0)`. Active-high synchronous `reset` to `"0000"`. The
            sequence is `0000, 0001, 0011, 0111, 1111, 1110, 1100, 1000, 0000, …`
        """,
        ports="clk, reset: in sl; q: out slv(3:0)",
        hints=["`q <= q(2 downto 0) & not q(3);`"],
    ),
    dict(
        num=13, name="onehot_ring", mode="seq",
        concept="a rotating one-hot token.",
        intro="""
            A ring counter rotates a single `'1'` around a register: each state is already
            one-hot decoded, which makes it handy for sequencing.
        """,
        verilog="`q <= {q[6:0], q[7]};`",
        task="8-bit one-hot ring counter. Active-high synchronous `reset` to `\"00000001\"`. On each edge where `en = '1'`, rotate left by one (bit 7 wraps to bit 0).",
        ports="clk, reset, en: in sl; q: out slv(7:0)",
        hints=["`q(6 downto 0) & q(7)`, or `rotate_left` from `numeric_std` on an `unsigned`."],
    ),
    dict(
        num=14, name="pwm8", mode="seq", numeric=True,
        concept="a free-running counter compared against a duty value.",
        intro="""
            Pulse-width modulation: a counter runs freely, and the output is high while the
            counter is below a threshold. The fraction of time spent high is
            `duty / 256`.
        """,
        verilog="Same.",
        task="""
            An 8-bit counter increments every cycle and wraps 255 → 0; active-high
            synchronous `reset` clears it. `pwm` is `'1'` when `counter < duty`, compared
            combinationally against the current `duty` input.
        """,
        ports="clk, reset: in sl; duty: in slv(7:0); pwm: out sl",
        options={"cycles": 800, "reset_prob": 0.002},
        hints=["`pwm <= '1' when cnt < unsigned(duty) else '0';`"],
    ),
]
