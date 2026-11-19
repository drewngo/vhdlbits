# 16.9 bug_multiple_drivers

**New concept:** debugging a register with two controls.

This file is a complete design that compiles, but it has a bug. The task below says what
the design is **supposed** to do. Find the bug with the grader and the waveform, and fix
it, changing as little as possible.

**Coming from Verilog:** Bugs like this one exist in Verilog too; the VHDL symptoms are what's worth learning to recognize.

## Task

An 8-bit register `q`. At each rising edge: if `clear = '1'`, `q` becomes 0;
otherwise if `load = '1'`, `q` takes `d`; otherwise it holds. (`clear` has
priority.)

## Ports

```vhdl
entity top_module is
  port (
    clk, clear, load : in  std_logic;
    d                : in  std_logic_vector(7 downto 0);
    q                : out std_logic_vector(7 downto 0)
  );
end entity top_module;
```

The grader asserts `clear` in the first cycle so the register starts known.

## Hints

<details><summary>Hint 1</summary>

Look for `'X'` in the waveform. Every process that assigns a signal is a driver of it.

</details>

## Check

```
./check.py 16.9
```
