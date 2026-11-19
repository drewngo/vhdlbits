# 6.1 unsigned_add

**New concept:** `ieee.numeric_std`, converting `slv ↔ unsigned`, `resize`. Never use `std_logic_arith`.

`std_logic_vector` is just a bag of bits: it has no arithmetic. `ieee.numeric_std`
adds two types with the same elements but numeric meaning, `unsigned` and
`signed`, plus the operators and conversions:

```vhdl
use ieee.numeric_std.all;
...
total <= std_logic_vector(unsigned(x) + unsigned(z));    -- slv -> unsigned -> slv
wider <= resize(unsigned(x), 12);                        -- zero-extend to 12 bits
```

Converting between `std_logic_vector` and `unsigned`/`signed` is a plain type
conversion because they're closely related array types. The result of `+` is as
wide as the wider operand, so to keep a carry you widen an operand *first*.

You'll see `ieee.std_logic_arith` and `std_logic_unsigned` in old code. They're
vendor packages, not IEEE standards; don't use them in new designs.

**Coming from Verilog:** Verilog vectors are implicitly unsigned numbers. In VHDL you choose `unsigned` or `signed` explicitly, and widths never grow automatically.

## Task

Add the two 8-bit unsigned numbers `a` and `b` and output the full 9-bit result (including the carry) on `sum`.

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

`resize(unsigned(a), 9) + unsigned(b)` is 9 bits wide.

</details>

<details><summary>Hint 2</summary>

Convert back with `std_logic_vector(...)`.

</details>

## Check

```
./check.py 6.1
```
