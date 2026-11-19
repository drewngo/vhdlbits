# 6.9 integer_range

**New concept:** internal `integer range 0 to 99` signals and saturating logic.

An `integer` signal with a range constraint synthesizes to just enough bits, and
the simulator checks the range: assigning 100 to a `range 0 to 99` signal is a
runtime error. That catches bugs early.

```vhdl
signal level : integer range 0 to 15;
...
level <= to_integer(unsigned(raw));
out_v <= std_logic_vector(to_unsigned(level, 4));
```

**Coming from Verilog:** No equivalent: Verilog integers are just 32-bit regs. VHDL range-checks them in simulation.

## Task

Convert `a` and `b` to integers, add them, saturate at 99, and output the result as
a 7-bit unsigned value on `s`. Inputs are always 0–99.

## Ports

```vhdl
entity top_module is
  port (
    a, b : in  std_logic_vector(6 downto 0);
    s    : out std_logic_vector(6 downto 0)
  );
end entity top_module;
```

The grader only drives values from 0 to 99.

## Hints

<details><summary>Hint 1</summary>

The raw sum needs a bigger range than 0 to 99 (up to 198), so use a variable or signal with `range 0 to 198` for it.

</details>

<details><summary>Hint 2</summary>

`to_unsigned(n, 7)` converts back.

</details>

## Check

```
./check.py 6.9
```
