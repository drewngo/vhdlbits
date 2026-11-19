# 7.2 full_adder

**New concept:** adding a carry-in.

A full adder adds three bits. The sum is the XOR of all three; the carry-out is
`'1'` when at least two inputs are `'1'` (the majority function from 2.12).

**Coming from Verilog:** Same gates; remember the parentheses around each product term.

## Task

Add `a`, `b` and `cin`: `s` is the sum bit, `cout` the carry-out.

## Ports

```vhdl
entity top_module is
  port (
    a, b, cin : in  std_logic;
    s, cout   : out std_logic
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

`cout` is the majority of the three inputs.

</details>

## Check

```
./check.py 7.2
```
