# 16.10 bug_integer_overflow

**New concept:** debugging a counting loop.

This file is a complete design that compiles, but it has a bug. The task below says what
the design is **supposed** to do. Find the bug with the grader and the waveform, and fix
it, changing as little as possible.

**Coming from Verilog:** Bugs like this one exist in Verilog too; the VHDL symptoms are what's worth learning to recognize.

## Task

`count` is the number of `'1'` bits in the 32-bit `din` (0–32).

## Ports

```vhdl
entity top_module is
  port (
    din   : in  std_logic_vector(31 downto 0);
    count : out std_logic_vector(5 downto 0)
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

Read GHDL's runtime error message carefully: which value didn't fit?

</details>

## Check

```
./check.py 16.10
```
