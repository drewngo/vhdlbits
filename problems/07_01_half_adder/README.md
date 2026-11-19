# 7.1 half_adder

**New concept:** the smallest arithmetic circuit.

A half adder adds two bits. The sum bit is the XOR, and the carry is the AND.
Every bigger adder is built from this idea.

**Coming from Verilog:** `assign {c, s} = a + b;` works in Verilog because the target width grows the add. In VHDL, write the gates or use `numeric_std` with explicit widths.

## Task

Add `a` and `b`: `s` is the sum bit, `c` the carry.

## Ports

```vhdl
entity top_module is
  port (
    a, b : in  std_logic;
    s, c : out std_logic
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

Two gates.

</details>

## Check

```
./check.py 7.1
```
