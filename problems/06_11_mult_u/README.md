# 6.11 mult_u

**New concept:** `*` result width is the sum of the operand widths.

`unsigned * unsigned` returns a result as wide as both operands combined, so an
8×8 product is 16 bits with no resizing needed:

```vhdl
area <= std_logic_vector(unsigned(w) * unsigned(h));
```

(Contrast with `+`, which does *not* grow.)

**Coming from Verilog:** In Verilog the target width decides; in VHDL the operands do, and the target must match exactly.

## Task

Multiply the 8-bit unsigned `a` and `b` into the 16-bit product `p`.

## Ports

```vhdl
entity top_module is
  port (
    a, b : in  std_logic_vector(7 downto 0);
    p    : out std_logic_vector(15 downto 0)
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

One line.

</details>

## Check

```
./check.py 6.11
```
