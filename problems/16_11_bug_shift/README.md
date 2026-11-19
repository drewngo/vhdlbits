# 16.11 bug_shift

**New concept:** debugging a shift.

This file is a complete design that compiles, but it has a bug. The task below says what
the design is **supposed** to do. Find the bug with the grader and the waveform, and fix
it, changing as little as possible.

**Coming from Verilog:** Bugs like this one exist in Verilog too; the VHDL symptoms are what's worth learning to recognize.

## Task

`y = x / 4` for the 8-bit signed `x`, rounding toward −∞ (an arithmetic shift right by 2).

## Ports

```vhdl
entity top_module is
  port (
    x : in  std_logic_vector(7 downto 0);
    y : out std_logic_vector(7 downto 0)
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

Two things are wrong with that one operator: the direction, and what fills the vacated bits.

</details>

## Check

```
./check.py 16.11
```
