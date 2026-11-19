# 16.3 bug_signal_vs_var

**New concept:** debugging a clocked accumulator.

This file is a complete design that compiles, but it has a bug. The task below says what
the design is **supposed** to do. Find the bug with the grader and the waveform, and fix
it, changing as little as possible.

**Coming from Verilog:** Bugs like this one exist in Verilog too; the VHDL symptoms are what's worth learning to recognize.

## Task

A running total: at each rising edge, `total ← total + x` (12 bits, wrapping).
`over` is registered and is `'1'` after an edge exactly when the **new** total is
2048 or more. Active-high synchronous `reset` clears `total` and `over`.

## Ports

```vhdl
entity top_module is
  port (
    clk, reset : in  std_logic;
    x          : in  std_logic_vector(7 downto 0);
    total      : out std_logic_vector(11 downto 0);
    over       : out std_logic
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

Which value of `acc` does the comparison see: before or after this edge's addition?

</details>

## Check

```
./check.py 16.3
```
