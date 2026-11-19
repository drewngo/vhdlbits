# 16.5 bug_resize

**New concept:** debugging an adder.

This file is a complete design that compiles, but it has a bug. The task below says what
the design is **supposed** to do. Find the bug with the grader and the waveform, and fix
it, changing as little as possible.

**Coming from Verilog:** Bugs like this one exist in Verilog too; the VHDL symptoms are what's worth learning to recognize.

## Task

`sum = a + b` for 8-bit unsigned inputs, as a full 9-bit result.

## Ports

```vhdl
entity top_module is
  port (
    a, b : in  std_logic_vector(7 downto 0);
    sum  : out std_logic_vector(8 downto 0)
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

How wide is `unsigned(a) + unsigned(b)`?

</details>

## Check

```
./check.py 16.5
```
