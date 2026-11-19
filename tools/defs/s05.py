SECTION = 5

PROBLEMS = [
    dict(
        num=1, name="comb_process",
        concept="`process(all)` (VHDL-2008) is the equivalent of `always @(*)`.",
        intro="""
            A **process** is a block of *sequential* statements (`if`, `case`, loops) that
            re-runs whenever something in its sensitivity list changes. `process(all)` means
            "every signal read inside", which is what you want for combinational logic.

            ```vhdl
            process(all)
            begin
              alarm <= smoke or heat;
            end process;
            ```

            The process as a whole is still one concurrent statement, side by side with
            ordinary `<=` assignments in the architecture.
        """,
        verilog="`always @(*)` becomes `process(all)`, and `begin ... end` becomes `begin ... end process;`. Inside a process, `<=` is still the signal assignment.",
        task="Compute `a AND b` twice: once as a concurrent assignment (`y_conc`) and once inside a `process(all)` (`y_proc`).",
        ports="a, b: in sl; y_conc, y_proc: out sl",
        hints=["The process body is a single line, the same as the concurrent one."],
    ),
    dict(
        num=2, name="clocked_process", mode="seq",
        concept="`process(clk)` + `if rising_edge(clk) then`.",
        intro="""
            A flip-flop is a process that only acts on a clock edge:

            ```vhdl
            process(clk)
            begin
              if rising_edge(clk) then
                q <= d;
              end if;
            end process;
            ```

            `rising_edge(clk)` is true only during the simulation cycle in which `clk` goes
            from `'0'` to `'1'`. Every signal assigned inside that `if` becomes a register.
        """,
        verilog="`always @(posedge clk) q <= d;` becomes the process above.",
        task="""
            Compute `a XOR b` three ways: concurrently (`y_conc`), in a combinational
            `process(all)` (`y_comb`), and registered in a clocked process (`y_ff`).

            `y_conc` and `y_comb` are identical; `y_ff` lags by one clock.
        """,
        ports="clk, a, b: in sl; y_conc, y_comb, y_ff: out sl",
        hints=["Three statements: one concurrent assignment and two processes."],
    ),
    dict(
        num=3, name="if_mux",
        concept="`when ... else` (concurrent) vs. `if/elsif/else` (in a process).",
        intro="""
            The same choice can be written two ways. Outside a process, a **conditional
            signal assignment**:

            ```vhdl
            led <= '1' when error = '1' else blink;
            ```

            Inside a process, an `if` statement:

            ```vhdl
            process(all)
            begin
              if error = '1' then
                led <= '1';
              else
                led <= blink;
              end if;
            end process;
            ```

            Conditions must be `boolean`: write `error = '1'`, not just `error`.
            (VHDL-2008 does allow `if error then` for `std_logic` via the `??` condition
            operator, but the explicit form is clearer.)
        """,
        verilog="`assign y = c ? b : a;` becomes `y <= b when c = '1' else a;`.",
        task="""
            Select `b` when both `sel1` and `sel2` are `'1'`, otherwise select `a`. Produce the
            same result twice: `y_when` with a conditional assignment and `y_if` with an `if`
            in a process.
        """,
        ports="a, b, sel1, sel2: in sl; y_when, y_if: out sl",
        hints=["The condition is `sel1 = '1' and sel2 = '1'`, a boolean expression."],
    ),
    dict(
        num=4, name="case_mux",
        concept="`case` statements need `when others`, because a `std_logic_vector` has 9^n possible values.",
        intro="""
            A `case` statement inside a process picks one branch by value:

            ```vhdl
            case code is
              when "00"   => color <= RED_RGB;
              when "01"   => color <= GREEN_RGB;
              when others => color <= BLACK_RGB;
            end case;
            ```

            The choices must cover **every** possible value of the selector. A 2-bit
            `std_logic_vector` has 81 values (`"UX"`, `"Z1"`, ...), so `when others` is
            effectively mandatory. Several values can share a branch with `|`:
            `when "10" | "11" =>`.
        """,
        verilog="Verilog's `default:` is `when others =>`, and it's required here, not optional.",
        task="""
            Build a 6-to-1 mux of 4-bit inputs selected by `sel` (0 → `d0` … 5 → `d5`). If
            `sel` is 6 or 7, output `"0000"`.
        """,
        ports="sel: in slv(2:0); d0, d1, d2, d3, d4, d5: in slv(3:0); y: out slv(3:0)",
        hints=["Six explicit choices `\"000\"` … `\"101\"` and one `when others => y <= \"0000\";`."],
    ),
    dict(
        num=5, name="priority_encoder",
        concept="VHDL-2008 matching case `case? ... is` with `'-'` don't-cares. This replaces Verilog's `casez`.",
        intro="""
            In a normal `case`, `'-'` is just another literal value. The VHDL-2008 **matching
            case**, `case?`, treats `'-'` in a choice as "matches anything":

            ```vhdl
            case? req is
              when "1--" => grant <= "100";
              when "01-" => grant <= "010";
              when "001" => grant <= "001";
              when others => grant <= "000";
            end case?;
            ```

            Choices are checked as a set, not in order, so they must not overlap. Write them
            so that each input pattern matches exactly one choice.
        """,
        verilog="`casez` with `?` becomes `case?` with `'-'`. Unlike `casez`, overlapping choices are an error, not a priority list.",
        task="Output on `pos` the index of the **lowest** set bit of the 8-bit input `din`, or 0 if no bit is set.",
        ports="din: in slv(7:0); pos: out slv(2:0)",
        hints=[
            "Bit 0 set means `pos = 0` regardless of the others: `when \"-------1\" =>`.",
            "The next choice is `\"------10\"`, and so on.",
        ],
    ),
    dict(
        num=6, name="no_latches",
        concept="default assignments at the top of a combinational process, so incomplete branches can't infer latches.",
        intro="""
            In a combinational process, every output must be assigned on every path. If some
            path skips an output, the process has to *remember* its old value, and synthesis
            infers a latch.

            The clean fix is to assign defaults first and override them in the branches.
            Within one pass of a process the last assignment wins, so this is safe:

            ```vhdl
            process(all)
            begin
              buzz  <= '0';
              flash <= '0';
              if alarm = '1' then
                buzz <= '1';
              end if;
            end process;
            ```
        """,
        verilog="Same rule as `always @(*)`: assign everything on every path. Defaults at the top are the usual idiom in both languages.",
        task="""
            Decode a 4-bit opcode into control lines. Every output defaults to `'0'`.

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
        hints=["Six default assignments, then a `case op is` whose `when others => null;` is now safe."],
    ),
    dict(
        num=7, name="variables_vs_signals", mode="seq",
        concept="inside a clocked process, a `variable` updates immediately (like blocking `=`) while a `signal` updates at the end of the process (like nonblocking `<=`).",
        intro="""
            A **variable** is declared inside a process and assigned with `:=`. The new value
            is visible on the very next line. A **signal** assignment `<=` only schedules
            the new value; the process keeps seeing the old value until it suspends.

            ```vhdl
            process(clk)
              variable v : unsigned(3 downto 0);
            begin
              if rising_edge(clk) then
                v := cnt + 1;      -- v has the new value right now
                cnt <= v;          -- cnt changes after this process suspends
                big <= v(3);       -- uses this cycle's v
              end if;
            end process;
            ```

            A signal assigned inside a clocked process is a register. Reading it back in the
            same process gives last cycle's value, which adds one cycle of delay.
        """,
        verilog="A variable behaves like a blocking `=`, and a signal like a nonblocking `<=`. Unlike Verilog, the two can't be mixed up, because they are different kinds of object.",
        task="""
            One clocked process. On every rising edge:

            - `y_var` registers `(a XOR b) AND c`, with `a XOR b` held in an intermediate
              **variable** (so it's this cycle's value).
            - `y_sig` does the same calculation through an intermediate **signal** assigned in
              the same clocked process. It therefore uses the *previous* cycle's `a XOR b`.

            ```
            clk edge    :   1     2     3     4
            a xor b     :   1     0     1     1
            c           :   1     1     1     0
            t (signal)  :   ?  →  1  →  0  →  1  →  1   (t takes a xor b at each edge)
            y_var after :   1     0     1     0         ((a xor b) and c, same edge)
            y_sig after :   ?     1     0     0         (old t and c)
            ```

            `y_sig` is what you get when you meant `y_var`. That's one of the most common VHDL
            bugs (see 16.3).
        """,
        ports="clk, a, b, c: in sl; y_var, y_sig: out sl",
        hints=[
            "Declare `variable v : std_logic;` between `process(clk)` and `begin`, and `signal t : std_logic;` in the architecture.",
            "Inside `if rising_edge(clk)`: `v := a xor b; t <= a xor b; y_var <= v and c; y_sig <= t and c;`",
        ],
    ),
    dict(
        num=8, name="with_select",
        concept="concurrent selected assignment `with sel select y <= ...`.",
        intro="""
            `with ... select` is the concurrent cousin of `case`. It is a single statement,
            so it can live directly in the architecture body:

            ```vhdl
            with op select
              res <= x and z when "00",
                     x or z  when "01",
                     x xor z when others;
            ```

            The same coverage rule applies: `when others` is needed for `std_logic_vector`
            selectors.
        """,
        verilog="A `case` in an `always @(*)`, written without the process.",
        task="Build a 4-to-1 mux of 8-bit inputs `d0..d3` selected by `sel`, without a process.",
        ports="sel: in slv(1:0); d0, d1, d2, d3: in slv(7:0); y: out slv(7:0)",
        hints=["Four choices, the last as `when others`."],
    ),
    dict(
        num=9, name="case_ranges", numeric=True,
        concept="`case` on an integer with ranges (`when 48 to 57 =>`).",
        intro="""
            `case` choices on an integer can be ranges:

            ```vhdl
            case to_integer(unsigned(temp)) is
              when 0 to 15  => band <= "00";
              when 16 to 30 => band <= "01";
              when others   => band <= "11";
            end case;
            ```

            `to_integer(unsigned(...))` comes from `ieee.numeric_std`, which Section 6 covers
            properly. The stub already has `use ieee.numeric_std.all;`.
        """,
        verilog="Verilog `case` can't do ranges directly. Here the range is a single choice.",
        task="""
            Classify the ASCII byte `ch`:

            | `cls` | class |
            |---|---|
            | `"01"` | digit `'0'`–`'9'` (48–57) |
            | `"10"` | uppercase letter `'A'`–`'Z'` (65–90) |
            | `"11"` | lowercase letter `'a'`–`'z'` (97–122) |
            | `"00"` | anything else |
        """,
        ports="ch: in slv(7:0); cls: out slv(1:0)",
        hints=["`case to_integer(unsigned(ch)) is` with three ranges and `when others`."],
    ),
    dict(
        num=10, name="min4", numeric=True,
        concept="intermediate values in a process.",
        intro="""
            Variables are handy for multi-step combinational calculations: each step builds on
            the previous one without declaring a signal for every intermediate.

            ```vhdl
            process(all)
              variable best : unsigned(7 downto 0);
            begin
              best := unsigned(x);
              if unsigned(z) > best then best := unsigned(z); end if;
              biggest <= std_logic_vector(best);
            end process;
            ```

            `<` and `>` on `std_logic_vector` compare as *strings* of characters, which happens
            to work for equal lengths but is a bad habit. Convert to `unsigned` first.
        """,
        verilog="Comparisons on `std_logic_vector` aren't numeric. Cast to `unsigned`.",
        task="Output on `m` the minimum of four 8-bit unsigned values `a`, `b`, `c`, `d`.",
        ports="a, b, c, d: in slv(7:0); m: out slv(7:0)",
        hints=["A variable holding the running minimum, updated three times."],
    ),
    dict(
        num=11, name="last_assignment_wins",
        concept="in a process, only the last signal assignment in a pass takes effect.",
        intro="""
            A signal can be assigned several times in one pass of a process. Only the last
            assignment executed counts, because each one just overwrites the scheduled value.

            ```vhdl
            process(all)
            begin
              mode <= "00";
              if test = '1' then mode <= "11"; end if;   -- overrides the default
            end process;
            ```
        """,
        verilog="Same as several nonblocking assignments to one reg in an `always` block.",
        task="""
            `y` starts as `"00"`. Then: if `a = '1'`, set `y = "01"`; then if `b = '1'`, set
            `y = "10"`; then if `a = '1'` and `b = '1'`, set `y = "11"`. Write it as three
            separate `if`s, not `elsif`.
        """,
        ports="a, b: in sl; y: out slv(1:0)",
        hints=["Four assignments in a row: one default and three guarded ones."],
    ),
    dict(
        num=12, name="loop_exit", numeric=True,
        concept="`for` loops with `exit`; loops describe hardware, not runtime iteration.",
        intro="""
            A `for` loop in a process unrolls at synthesis. `exit` leaves the loop early, and
            the hardware it describes is a priority chain:

            ```vhdl
            for i in 0 to 7 loop
              if err(i) = '1' then
                first_err := i;
                exit;
              end if;
            end loop;
            ```

            The loop index is an `integer`; `to_unsigned(i, width)` converts it to a vector.
        """,
        verilog="`break` in a SystemVerilog loop is `exit` in VHDL.",
        options={"bias": {"din": 0.12}, "value_bias": {"din": [[0, 0.05]]}},
        task="Output on `idx` the index of the **highest** set bit of the 16-bit `din`, and `valid = '1'` if any bit is set. Output `idx = 0` when none are set.",
        ports="din: in slv(15:0); idx: out slv(3:0); valid: out sl",
        hints=[
            "Loop `for i in 15 downto 0`, and `exit` on the first `'1'`.",
            "Assign defaults (`idx <= \"0000\"; valid <= '0';`) before the loop.",
        ],
    ),
    dict(
        num=13, name="local_function",
        concept="declaring a `function` in the architecture's declarative region.",
        intro="""
            A function computes a value from its parameters. It can be declared where signals
            are, before `begin`. Parameters can be **unconstrained**, so one function handles
            any width:

            ```vhdl
            function ones(v : std_logic_vector) return natural is
              variable n : natural := 0;
            begin
              for i in v'range loop
                if v(i) = '1' then n := n + 1; end if;
              end loop;
              return n;
            end function;
            ```

            Use `v'range` inside, never fixed indices; a slice passed in might be
            `(15 downto 8)`.
        """,
        verilog="Like a Verilog `function`, but parameters can be unconstrained arrays.",
        task="""
            Write `function parity(v: std_logic_vector) return std_logic` that returns the XOR
            of all bits of `v`. Use it on both inputs: `pa = parity(a)`, `pb = parity(b)`.
        """,
        ports="a: in slv(7:0); b: in slv(15:0); pa, pb: out sl",
        hints=["A variable accumulator and `for i in v'range loop`. (`xor v` also works inside the function.)"],
    ),
    dict(
        num=14, name="procedure_swap", numeric=True,
        concept="a `procedure` with `out`/`inout` parameters inside a process.",
        intro="""
            A **procedure** is a subprogram that returns results through `out` or `inout`
            parameters instead of a return value. Declared inside a process, it can work on
            the process's variables:

            ```vhdl
            process(all)
              procedure clip(variable v : inout unsigned(7 downto 0)) is
              begin
                if v > 200 then v := to_unsigned(200, 8); end if;
              end procedure;
              variable t : unsigned(7 downto 0);
            begin
              t := unsigned(level);
              clip(t);
              out_level <= std_logic_vector(t);
            end process;
            ```
        """,
        verilog="Closest to a Verilog `task` with output arguments.",
        task="""
            Write a procedure `compare_swap(lo, hi)` that takes two `inout` 8-bit unsigned
            variables and swaps them if `lo > hi`. Use it three times to sort `x`, `y`, `z` so
            that `s0 ≤ s1 ≤ s2` (unsigned).
        """,
        ports="x, y, z: in slv(7:0); s0, s1, s2: out slv(7:0)",
        hints=[
            "A three-element sorting network: compare-swap (0,1), then (1,2), then (0,1) again.",
        ],
    ),
]
