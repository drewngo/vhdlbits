# 16.4 bug_numeric

**New concept:** debugging a comparison.

This file is a complete design that compiles, but it has a bug. The task below says what
the design is **supposed** to do. Find the bug with the grader and the waveform, and fix
it, changing as little as possible.

**Coming from Verilog:** Bugs like this one exist in Verilog too; the VHDL symptoms are what's worth learning to recognize.

## Task

`m` is the minimum of `a` and `b`, both 8-bit **signed** (two's complement).

## Ports

```vhdl
entity top_module is
  port (
    a, b : in  std_logic_vector(7 downto 0);
    m    : out std_logic_vector(7 downto 0)
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

Try `a = x"FF"` (−1) and `b = x"01"`.

</details>

## Check

```
./check.py 16.4
```
