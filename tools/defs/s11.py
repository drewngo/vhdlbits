import textwrap

SECTION = 11


def _indent(text):
    """Match the 12-space indentation of the intro strings these get appended to."""
    return textwrap.indent(textwrap.dedent(text), " " * 12)

FSM_PATTERN = _indent("""
    Throughout this section, the recommended pattern is:

    ```vhdl
    type state_t is (IDLE, BUSY, FINISH);
    signal state, next_state : state_t;
    ...
    -- 1. state register
    process(clk)
    begin
      if rising_edge(clk) then
        if reset = '1' then
          state <= IDLE;
        else
          state <= next_state;
        end if;
      end if;
    end process;

    -- 2. next-state and output logic
    process(all)
    begin
      next_state <= state;          -- default: stay
      done_flag  <= '0';            -- default outputs
      case state is
        when IDLE   => if go = '1' then next_state <= BUSY; end if;
        when BUSY   => ...
        when FINISH => done_flag <= '1'; next_state <= IDLE;
      end case;
    end process;
    ```

    A single clocked process that does everything is also fine, and often shorter for
    small machines. Outputs that must be registered (one cycle after the event) come
    naturally from that style.
""")

UART_COMMON = _indent("""
    The line `rxd` idles at `'1'` and carries one bit per clock (no oversampling): sample
    it once at every rising edge.
""")

PROBLEMS = [
    dict(
        num=1, name="fsm_toggle", mode="seq",
        concept="enum state type, two-process FSM.",
        intro="""
            A finite state machine in VHDL starts with an enumerated state type. The tools
            pick the encoding (binary, one-hot, …), and the waveform shows state *names*.
        """ + FSM_PATTERN,
        verilog="No more `localparam` state codes or `reg [1:0] state`: declare a `type` and let the tools encode it.",
        task="""
            Two states, off and on. At every rising edge where `t = '1'`, switch state.
            The output `y` is `'1'` in the on state (a Moore output: it depends only on the
            state). Active-high synchronous `reset` → off.

            Careful with names: `on` is a reserved word in VHDL (as in `wait on clk`), so
            `type state_t is (OFF, ON);` doesn't compile. Use names like `S_OFF`, `S_ON`.
        """,
        ports="clk, reset, t: in sl; y: out sl",
        hints=["`y <= '1' when state = S_ON else '0';`"],
    ),
    dict(
        num=2, name="fsm_mealy", mode="seq",
        concept="Mealy outputs depend on current inputs (checked by the mid-cycle compare).",
        intro="""
            A **Mealy** output depends on the state *and* the current inputs, so it can change
            in the middle of a clock cycle when an input changes. The grader compares outputs
            right after the inputs change, so a registered (Moore) version fails here.
        """,
        verilog="Same as an output computed in `always @(*)` from state and inputs.",
        task="Same states and transitions as 11.1, but `y = '1'` when the state is on **and** `t = '0'` in the current cycle.",
        ports="clk, reset, t: in sl; y: out sl",
        hints=["`y <= '1' when state = S_ON and t = '0' else '0';`"],
    ),
    dict(
        num=3, name="seq_1011", mode="seq",
        concept="sequence detector with overlap.",
        intro="""
            A sequence detector has one state per prefix of the pattern matched so far. On a
            mismatch, it doesn't always go back to the start: it goes to the longest suffix of
            what it has seen that is still a prefix of the pattern. That's what allows
            overlapping matches.
        """,
        verilog="Same design method.",
        task="""
            `din` is sampled at each rising edge. `found` is `'1'` during the cycle after the
            edge at which the last four samples were `1, 0, 1, 1` (oldest first). It's a Moore
            output. Overlap is allowed: the stream `1011011` produces two detections.
            Active-high synchronous `reset` forgets everything received so far.
        """,
        ports="clk, reset, din: in sl; found: out sl",
        hints=[
            "Five states: nothing, `1`, `10`, `101`, `1011`.",
            "From `1011`, a `1` leads to state `1` and a `0` leads to state `10`.",
        ],
    ),
    dict(
        num=4, name="walker", mode="seq",
        concept="states with priorities between inputs.",
        intro="""
            When several inputs can trigger transitions at once, write the priority into the
            order of the `if`/`elsif` chain, and handle the "both" case explicitly first.
        """,
        verilog="Same.",
        task="""
            A walker goes `LEFT` or `RIGHT`. At each rising edge:

            - `bump_l` and `bump_r` both `'1'`: reverse direction
            - only `bump_l`: go (or keep going) `RIGHT`
            - only `bump_r`: go (or keep going) `LEFT`
            - neither: keep going

            Outputs are one-hot: `go_l` is `'1'` in `LEFT`, `go_r` in `RIGHT`.
            **Asynchronous** active-high reset `areset` → `LEFT`.
        """,
        ports="clk, areset, bump_l, bump_r: in sl; go_l, go_r: out sl",
        hints=["The state register process tests `areset` before `rising_edge(clk)`."],
    ),
    dict(
        num=5, name="walker_fall", mode="seq",
        concept="adding states without breaking existing behavior.",
        intro="""
            Extending an FSM usually means adding states rather than flags. Here the walker
            needs to remember which way it was going while it falls, which is two new states,
            not one.
        """,
        verilog="Same.",
        task="""
            Extend 11.4 with a `ground` input. At each rising edge:

            - walking and `ground = '0'`: start falling (bumps are ignored on this edge)
            - walking and `ground = '1'`: same rules as 11.4
            - falling and `ground = '0'`: keep falling (bumps ignored)
            - falling and `ground = '1'`: resume walking in the direction it was going
              before the fall (bumps ignored on this edge)

            While falling, `go_l = go_r = '0'` and `falling = '1'`. Asynchronous active-high
            reset `areset` → walking `LEFT`.
        """,
        ports="clk, areset, bump_l, bump_r, ground: in sl; go_l, go_r, falling: out sl",
        options={"bias": {"ground": 0.85}},
        hints=["Four states: `LEFT`, `RIGHT`, `FALL_L`, `FALL_R`."],
    ),
    dict(
        num=6, name="debounce", mode="seq", numeric=True,
        concept="counter inside an FSM.",
        intro="""
            Mechanical switches bounce for milliseconds. A debouncer only accepts a new level
            after it has been stable for a while. A small counter does the timing; it
            restarts whenever the input agrees with the current output.
        """,
        verilog="Same.",
        task="""
            At each rising edge, compare `noisy` with `clean`:

            - if they're equal, the counter restarts
            - if they differ, the counter advances, and at the **4th consecutive edge** where
              they differ, `clean` takes the value of `noisy` (and the counter restarts)

            `clean` is a registered output. Active-high synchronous `reset` → `clean = '0'`,
            counter restarted.
        """,
        ports="clk, reset, noisy: in sl; clean: out sl",
        options={"reset_prob": 0.01, "cycles": 600},
        hints=["A counter `0 to 3`: flip `clean` when it is already 3 and the inputs still differ."],
    ),
    dict(
        num=7, name="uart_rx_byte", mode="seq",
        concept="framing FSM with a datapath.",
        intro="""
            Real protocols combine an FSM (where am I in the frame?) with a datapath (a shift
            register and a bit counter). Keep the bit counter as an integer signal alongside
            the state.
        """ + UART_COMMON,
        verilog="Same structure.",
        task="""
            - **Idle**: wait for a `'0'` (the start bit).
            - **Data**: the next 8 samples are the data bits, LSB first.
            - **Stop**: the next sample is the stop bit.
              - `'1'`: at that edge, copy the byte to `data` and set `done` (high for exactly
                the next cycle), then go back to idle (the very next sample may already be a
                new start bit).
              - `'0'`: framing error. Don't touch `data` or `done`; wait until a `'1'` is
                sampled, then go back to idle (that `'1'` can't also be a start bit).

            `done` is `'0'` after every other edge. `data` holds its value until the next good
            frame. Active-high synchronous `reset` → idle, `data = x"00"`, `done = '0'`.
        """,
        ports="clk, reset, rxd: in sl; data: out slv(7:0); done: out sl",
        options={"stimulus": "uart_frames", "stimulus_opts": {"port": "rxd"}, "cycles": 2000, "reset_prob": 0.002},
        after_ports="The grader feeds a mix of well-formed frames, frames with a bad stop bit, idle line, and noise.",
        hints=[
            "States: `IDLE`, `DATA` (with a bit counter 0–7), `STOP`, `WAIT_IDLE`.",
            "Shift right with the new bit entering at the top: after 8 shifts the first bit is in bit 0.",
        ],
    ),
    dict(
        num=8, name="handshake_fifo1", mode="seq",
        concept="valid/ready handshake, a one-entry buffer.",
        intro="""
            In a **valid/ready** handshake, a transfer happens on a clock edge where both
            `valid` (from the sender) and `ready` (from the receiver) are `'1'`. The sender
            must hold its data until then.

            A one-entry buffer is ready when it's empty, or when its current entry is being
            taken this very cycle. That second condition is combinational from the
            downstream `out_ready`, which lets data flow every cycle.
        """,
        verilog="Same protocol as AXI-Stream's TVALID/TREADY.",
        task="""
            One-entry buffer:

            - `out_valid = '1'` whenever the buffer holds an entry, with the entry on `out_data`
            - `in_ready = '1'` when the buffer is empty **or** `out_ready = '1'` (drained this cycle)
            - at a rising edge, the entry leaves if `out_valid = '1'` and `out_ready = '1'`,
              and `in_data` is stored if `in_valid = '1'` and `in_ready = '1'`; both can happen
              on the same edge
            - `out_data` keeps the last stored value while the buffer is empty

            Active-high synchronous `reset` → empty, `out_data = x"00"`.
        """,
        ports="clk, reset, in_valid, out_ready: in sl; in_data: in slv(7:0); in_ready, out_valid: out sl; out_data: out slv(7:0)",
        options={"bias": {"in_valid": 0.6, "out_ready": 0.5}, "reset_prob": 0.01},
        hints=["State is one `full` flag plus the stored byte. `in_ready <= not full or out_ready;`"],
    ),
    dict(
        num=9, name="onehot_next_state",
        concept="deriving next-state equations by hand for a one-hot encoding.",
        intro="""
            With one-hot encoding, each state has its own flip-flop. The next-state logic for
            state `S` is just "OR over every transition that enters `S`": for each source
            state and input condition that leads to `S`, AND the source's bit with the
            condition.
        """,
        verilog="Same derivation.",
        task="""
            This 4-state machine has input `x` and Moore output `y` (high in `D`):

            | state | next if `x = 0` | next if `x = 1` |
            |---|---|---|
            | A | A | B |
            | B | C | B |
            | C | A | D |
            | D | C | B |

            `state` is one-hot (`state(0)` = A, `state(1)` = B, `state(2)` = C, `state(3)` = D).
            Output the one-hot next state `nxt` and `y`. This is purely combinational.
        """,
        ports="state: in slv(3:0); x: in sl; nxt: out slv(3:0); y: out sl",
        options={"valid_inputs": "onehot(state)"},
        after_ports="The grader only drives one-hot values on `state`.",
        hints=["`nxt(0)` (A) is entered from A and C when `x = 0`: `(state(0) or state(2)) and not x`."],
    ),
    dict(
        num=10, name="binary_next_state", numeric=True,
        concept="the same machine with binary encoding.",
        intro="""
            With a binary encoding the next-state logic is a lookup on the state code and the
            input. A `case` on the state code is the direct translation.
        """,
        verilog="Same.",
        task="Same table as 11.9, but `state` is binary-encoded (A = `00`, B = `01`, C = `10`, D = `11`). Output the binary next state `nxt` and `y` (high in D).",
        ports="state: in slv(1:0); x: in sl; nxt: out slv(1:0); y: out sl",
        hints=["A `case` on `state` with an `if x` in each branch."],
    ),
    dict(
        num=11, name="fsm_from_table", mode="seq",
        concept="the full sequential machine from a table.",
        intro="""
            Now let the tools pick the encoding: declare an enum and transcribe the table.
        """,
        verilog="Same.",
        task="The machine from 11.9 as a real FSM with an enum state type. Output `y = '1'` in `D`. Active-high synchronous `reset` → `A`.",
        ports="clk, reset, x: in sl; y: out sl",
        hints=["Follow the two-process template from 11.1."],
    ),
    dict(
        num=12, name="header_packet", mode="seq",
        concept="byte-stream framing.",
        intro="""
            Many byte protocols mark the start of a packet with a header byte. The FSM hunts
            for the header, then counts payload bytes regardless of their value: a payload
            byte that happens to equal the header is still payload.
        """,
        verilog="Same.",
        task="""
            One byte arrives on `din` per cycle and is sampled at each rising edge.

            - While hunting, a byte equal to `x"A5"` starts a packet; any other byte is ignored.
            - The next two bytes are payload, whatever their value.
            - At the edge that samples the second payload byte, set `payload` to
              `first & second` (first byte in the upper half) and set `done`, which is high
              for exactly the next cycle. Then hunt again starting with the next byte.

            `done` is `'0'` after every other edge; `payload` holds until the next packet.
            Active-high synchronous `reset` → hunting, `payload = x"0000"`, `done = '0'`.
        """,
        ports="clk, reset: in sl; din: in slv(7:0); payload: out slv(15:0); done: out sl",
        options={"value_bias": {"din": [["A5", 0.15]]}},
        hints=["States `HUNT`, `B1`, `B2`; keep the first payload byte in a register."],
    ),
    dict(
        num=13, name="uart_rx_parity", mode="seq",
        concept="extending a protocol FSM.",
        intro="""
            Adding a field to a frame means one more state. With **odd** parity, the 8 data
            bits plus the parity bit contain an odd number of 1s.
        """ + UART_COMMON,
        verilog="Same.",
        task="""
            As 11.7, with an **odd** parity bit between the 8 data bits and the stop bit:
            start, 8 data bits (LSB first), parity, stop.

            - Stop bit `'1'` and parity correct: update `data` and pulse `done` as in 11.7.
            - Stop bit `'1'` but parity wrong: don't touch `data` or `done`; go straight back
              to idle.
            - Stop bit `'0'`: framing error, handled exactly as in 11.7 (wait for a `'1'`).

            Active-high synchronous `reset` → idle, `data = x"00"`, `done = '0'`.
        """,
        ports="clk, reset, rxd: in sl; data: out slv(7:0); done: out sl",
        options={"stimulus": "uart_frames", "stimulus_opts": {"port": "rxd", "parity": "odd"}, "cycles": 2000, "reset_prob": 0.002},
        after_ports="The grader's frames include bad parity bits and bad stop bits.",
        hints=["Start from your 11.7 solution and add a `PARITY` state; accumulate the XOR of the data bits as they arrive."],
    ),
    dict(
        num=14, name="bit_unstuff", mode="seq",
        concept="protocol FSM (HDLC-style bit stuffing).",
        intro="""
            HDLC marks frame boundaries with the flag `01111110`. To keep that pattern out of
            the data, the sender inserts (*stuffs*) a `0` after every five consecutive `1`s;
            the receiver removes it. Six `1`s in a row can only be a flag, and seven or more
            is an error (or an abort).
        """,
        verilog="Same.",
        task="""
            `din` is sampled at each rising edge. Count consecutive `1`s since the last `0`:

            - a `0` after exactly five `1`s: `discard` (the `0` was stuffed)
            - a `0` after exactly six `1`s: `flag`
            - a seventh consecutive `1`: `err`; after that, ignore the input until a `0` is
              sampled (that `0` restarts counting, and is not a discard or a flag)

            Each output is high for exactly the one cycle after the edge that completed its
            pattern (Moore). A `0` that triggers `discard` or `flag` also restarts counting.
            Active-high synchronous `reset` behaves as if a `0` had just been received.
        """,
        ports="clk, reset, din: in sl; discard, flag, err: out sl",
        options={"bias": {"din": 0.8}, "reset_prob": 0.01, "cycles": 1000},
        hints=[
            "States for 0–6 ones seen, plus `S_DISC`, `S_FLAG`, `S_ERR` and an error-wait state. (A state called `ERR` would clash with the port `err`: VHDL names are case-insensitive.)",
            "`S_DISC` and `S_FLAG` behave like \"0 ones seen\" for their next transition.",
        ],
    ),
    dict(
        num=15, name="vending", mode="seq",
        concept="an FSM whose states are amounts.",
        intro="""
            When the states represent an accumulated quantity, name them after the quantity
            (`C0`, `C5`, `C10`). The transitions then read like arithmetic.
        """,
        verilog="Same.",
        task="""
            Coins are sampled at each rising edge: `nickel` (5¢) or `dime` (10¢), never both
            in the same cycle. The machine accumulates the total. At the edge where a coin
            brings the total to 15¢ or more, set `vend` for exactly the next cycle, also set
            `change` for that cycle if the total became 20¢, and return the total to 0¢.
            Both outputs are `'0'` after every other edge. Active-high synchronous `reset` →
            0¢, outputs `'0'`.
        """,
        ports="clk, reset, nickel, dime: in sl; vend, change: out sl",
        options={"exclusive": [["nickel", "dime"]], "bias": {"nickel": 0.35, "dime": 0.35}},
        after_ports="The grader never drives `nickel` and `dime` high together.",
        hints=["Three amount states plus registered `vend`/`change`, or two extra output states."],
    ),
    dict(
        num=16, name="traffic_light", mode="seq", numeric=True,
        concept="FSM with an internal timer.",
        intro="""
            Many FSMs stay in a state for a fixed time. A timer that restarts on every state
            change keeps the timing logic out of the state type.
        """,
        verilog="Same.",
        task="""
            Four phases, with a timer `t` that is 0 in the first cycle of every phase and
            counts up by one each cycle:

            | phase | lights on | leaves at the edge where |
            |---|---|---|
            | `MAIN_GREEN` | `main_g`, `side_r` | `car_side = '1'` and `t ≥ 4` (green for at least 5 cycles) |
            | `MAIN_YELLOW` | `main_y`, `side_r` | `t = 1` (2 cycles) |
            | `SIDE_GREEN` | `main_r`, `side_g` | `t = 3` (4 cycles) |
            | `SIDE_YELLOW` | `main_r`, `side_y` | `t = 1` (2 cycles) |

            The phases cycle in that order. All other light outputs are `'0'` (Moore).
            Active-high synchronous `reset` → `MAIN_GREEN` with `t = 0`.

            Don't name a state `MAIN_G`: VHDL is case-insensitive, so it would clash with the
            port `main_g`.
        """,
        ports="clk, reset, car_side: in sl; main_g, main_y, main_r, side_g, side_y, side_r: out sl",
        options={"bias": {"car_side": 0.3}, "reset_prob": 0.01, "cycles": 600},
        hints=["In `MAIN_GREEN` the timer can saturate at 4; nothing needs it to count higher."],
    ),
    dict(
        num=17, name="arbiter_fixed3", mode="seq",
        concept="fixed-priority arbitration with grant hold.",
        intro="""
            An arbiter gives a shared resource to one requester at a time. With **grant
            hold**, a requester keeps the grant until it lets go, even if someone with
            higher priority asks in the meantime.
        """,
        verilog="Same.",
        task="""
            Three requesters, `req(0)` highest priority. `gnt` is a registered one-hot vector
            (or all zeros). At each rising edge:

            - if a grant is held and that requester's `req` is still `'1'`, keep it
            - otherwise grant the highest-priority requester whose `req` is `'1'` (lowest
              index), or nobody

            Active-high synchronous `reset` → no grant.
        """,
        ports="clk, reset: in sl; req: in slv(2:0); gnt: out slv(2:0)",
        options={"bias": {"req": 0.5}},
        hints=["`if (gnt and req) /= \"000\" then` keeps the current grant."],
    ),
    dict(
        num=18, name="arbiter_rr2", mode="seq",
        concept="round-robin fairness.",
        intro="""
            A round-robin arbiter remembers who it served last and gives the other requester
            priority next time, so nobody starves.
        """,
        verilog="Same.",
        task="""
            Two requesters. `gnt` is registered and recomputed at every rising edge from the
            current `req`, so each grant lasts one cycle:

            - only one requester: grant it
            - both: grant the one that was **not** granted most recently
            - neither: no grant

            "Most recently granted" is updated on every edge that grants somebody. After
            reset, requester 0 wins the first tie. Active-high synchronous `reset` → no
            grant.
        """,
        ports="clk, reset: in sl; req: in slv(1:0); gnt: out slv(1:0)",
        hints=["One extra flag remembers who was granted last; reset it as if requester 1 had just been served."],
    ),
    dict(
        num=19, name="detect_then_enable", mode="seq",
        concept="chaining a detector FSM with a fixed-length action.",
        intro="""
            A common structure: an FSM hunts for a trigger, performs a fixed-length action,
            then starts hunting again. During the action the input is ignored.
        """,
        verilog="Same.",
        task="""
            `din` is sampled at each rising edge. When the last three samples are `1, 1, 0`
            (oldest first), `go` is `'1'` for exactly the next 3 cycles (Moore). Samples taken
            at the edges that end those 3 cycles are ignored; after that the search starts
            from scratch. Overlap with bits before the trigger is allowed (e.g. `1110`
            triggers). Active-high synchronous `reset` → searching from scratch.
        """,
        ports="clk, reset, din: in sl; go: out sl",
        hints=["Search states for nothing, `1`, `11`, then three `GO` states."],
    ),
    dict(
        num=20, name="timer_unit", mode="seq", numeric=True,
        concept="a full control unit made of a detector, a shift-in, a counter, and an ack handshake.",
        intro="""
            Bigger controllers are several small machines in sequence. Write each phase as a
            group of states, and give the datapath (shift register, counters) its own
            registers.
        """,
        verilog="Same.",
        task="""
            `din` and `ack` are sampled at each rising edge.

            1. **Search** for `1, 1, 0, 1` on `din` (overlapping matches allowed while searching).
            2. **Shift in** the next 4 samples of `din`, MSB first, as `delay`.
            3. **Count** for `(delay + 1) × 10` cycles with `counting = '1'`. During the first 10
               of those cycles `remaining = delay`, during the next 10 `remaining = delay - 1`,
               …, during the last 10 `remaining = 0`.
            4. **Done**: `done = '1'` until an edge samples `ack = '1'`; then go back to
               searching from scratch.

            `counting` and `done` are Moore outputs. `remaining` is `"0000"` whenever
            `counting = '0'`. Active-high synchronous `reset` → searching from scratch.
        """,
        ports="clk, reset, din, ack: in sl; counting, done: out sl; remaining: out slv(3:0)",
        options={"bias": {"ack": 0.2}, "cycles": 20000, "reset_prob": 0.0005},
        hints=[
            "Two counters while counting: `remaining` (tens) and a 0–9 sub-counter.",
            "The count phase ends at the edge where the sub-counter is 9 and `remaining` is 0.",
        ],
    ),
    dict(
        num=21, name="elevator3", mode="seq", numeric=True,
        concept="request latching, direction preference, and a precise spec.",
        intro="""
            Controllers with "nearest", "prefer" and "while" in their description are easy to
            get almost right. Before writing any VHDL, make sure the spec answers every
            *what happens if…* question. This one tries to.
        """,
        verilog="Same.",
        task="""
            A car serves floors 0–2. State: `floor`, a 3-bit pending-request set `p`, a
            direction `dir` (`UP` or `DOWN`), and a phase `IDLE`, `DOOR`, `MOVE1` or `MOVE2`.

            At every rising edge, first merge new calls: `P = p or call`. Then, by phase:

            - **IDLE**: run *decide* (below) at the current floor.
            - **DOOR**: go to `IDLE`; `p ← P` with the current floor's bit cleared (a call for
              the floor whose door is open is served by that opening).
            - **MOVE1**: go to `MOVE2`; `p ← P`.
            - **MOVE2**: `floor` moves one floor in direction `dir`, then run *decide* at the
              new floor.

            *decide* at floor `f`, in this order:

            1. `P(f) = '1'`: go to `DOOR`, `p ← P` with bit `f` cleared.
            2. there is a request in direction `dir` (above `f` for `UP`, below for `DOWN`):
               go to `MOVE1`, `p ← P`.
            3. there is a request in the other direction: flip `dir`, go to `MOVE1`, `p ← P`.
            4. otherwise go to `IDLE`, `p ← P` (which is all zeros here).

            Outputs (Moore): `floor` as a binary number, `door = '1'` in `DOOR`.
            Active-high synchronous `reset` → floor 0, `p = "000"`, `dir = UP`, `IDLE`.

            So a move takes 2 cycles per floor, a stop adds one `DOOR` cycle and one `IDLE`
            cycle, and the car never stops at a floor nobody asked for.
        """,
        ports="clk, reset: in sl; call: in slv(2:0); floor: out slv(1:0); door: out sl",
        options={"bias": {"call": 0.06}, "reset_prob": 0.005, "cycles": 2000},
        hints=[
            "Write *decide* as a procedure (or just repeat it) used in both `IDLE` and `MOVE2`.",
            "Keep `p` as a `std_logic_vector(2 downto 0)` and the floor as an integer `0 to 2`.",
        ],
    ),
    dict(
        num=22, name="wave_puzzle_seq1", mode="seq",
        concept="reverse-engineering a sequential circuit from a waveform.",
        intro="""
            7.15 recovered a truth table from a trace. With a clock, an output can depend on
            earlier inputs too, so read the waveform edge by edge: at each rising edge, which
            inputs (now and at earlier edges) decide what `q` becomes?
        """,
        verilog="Nothing language-specific here.",
        task="""
            Build the circuit that produced this waveform. `reset` is synchronous and active
            high, and clears everything. The waveform was drawn by simulating the reference
            answer, so it is exact.
        """,
        ports="clk, reset, a: in sl; q: out sl",
        hints=[
            "Find the edges where `q` becomes 1. What was `a` at that edge, and at the edge before?",
            "One flip-flop remembers the previous `a`, a second one is `q`.",
        ],
    ),
    dict(
        num=23, name="wave_puzzle_seq2", mode="seq",
        concept="telling registered outputs from combinational ones in a waveform.",
        intro="""
            An output that changes only at rising edges is registered. One that also changes
            when an input does, between edges, is (at least partly) combinational: a Mealy
            output.
        """,
        verilog="Nothing language-specific here.",
        task="""
            Build the circuit that produced this waveform: one output is a flip-flop and the
            other is combinational. `reset` is synchronous and active high, and clears the
            flip-flop.
        """,
        ports="clk, reset, a, b: in sl; p, q: out sl",
        hints=[
            "`q` only moves at rising edges. At which edges does it change, and what are `a` and `b` there?",
            "`p` changes whenever `b` or `q` does. Compare `p` with `q` while `b = 0`, then while `b = 1`.",
        ],
    ),
    dict(
        num=24, name="wave_puzzle_seq3", mode="seq", numeric=True,
        concept="reverse-engineering a counter from a waveform.",
        intro="""
            Bus values in a waveform are often counts. Look at how the value moves from edge to
            edge, and pay attention to what happens at the ends of its range.
        """,
        verilog="Nothing language-specific here.",
        task="""
            Build the circuit that produced this waveform (values of `q` are shown in decimal).
            `reset` is synchronous and active high, and sets `q` to 0.
        """,
        ports="clk, reset, x: in sl; q: out slv(2:0)",
        options={"stimulus": "runs", "stimulus_opts": {"port": "x", "min": 1, "max": 10}},
        hints=[
            "Which way does `q` move when `x = 1`? When `x = 0`?",
            "`q` never goes below 0, and never above one particular value: it saturates instead of wrapping.",
        ],
    ),
    dict(
        num=25, name="wave_puzzle_seq4", mode="seq",
        concept="reverse-engineering a small state machine from a waveform.",
        intro="""
            A state machine shows up in a waveform as an output that depends on *how* the
            inputs got where they are. Line up each pulse of the output with the history of
            the input just before it.
        """,
        verilog="Nothing language-specific here.",
        task="""
            Build the circuit that produced this waveform. `z` is a Moore output (it changes
            only at rising edges). `reset` is synchronous and active high.
        """,
        ports="clk, reset, x: in sl; z: out sl",
        options={"stimulus": "runs", "stimulus_opts": {"port": "x", "min": 1, "max": 5}},
        hints=[
            "`z` pulses right after `x` falls, but not every time. Count how many edges `x` was high before each fall.",
            "Count consecutive edges with `x = 1`, saturating at the threshold you found; check the count when `x` is 0.",
        ],
    ),
]
