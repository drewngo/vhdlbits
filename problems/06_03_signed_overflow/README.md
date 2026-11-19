# 6.3 signed_overflow

**New concept:** two's-complement overflow detection.

Adding two `signed` values of the same width wraps around silently. Overflow
happens exactly when both operands have the same sign and the result's sign is
different. (Equivalently: compute one bit wider and check whether the top two bits
of the wide result disagree.)

```vhdl
-- sign bits of operands and result
wrapped <= (x(7) and z(7) and not r(7)) or (not x(7) and not z(7) and r(7));
```

**Coming from Verilog:** Same rule as in Verilog; here `+` on two 8-bit `signed` gives an 8-bit result.

## Task

`s = a + b` (8-bit signed, wrapping). `ovf = '1'` when the true sum doesn't fit in 8 signed bits.

## Ports

```vhdl
entity top_module is
  port (
    a, b : in  std_logic_vector(7 downto 0);
    s    : out std_logic_vector(7 downto 0);
    ovf  : out std_logic
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

Compare the sign bits of `a`, `b`, and the 8-bit sum.

</details>

## Check

```
./check.py 6.3
```
