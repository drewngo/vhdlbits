# 6.14 sat_add_s

**New concept:** saturating arithmetic.

DSP code often clamps instead of wrapping. One approach: add one bit wider, then
compare the wide result against the limits.

```vhdl
wide := resize(signed(x), 9) + resize(signed(z), 9);
if wide > 127 then ...
```

Comparing a `signed` with an integer literal (`wide > 127`) is defined in
`numeric_std`.

**Coming from Verilog:** Same technique; widen first so the true sum is representable.

## Task

8-bit signed addition that clamps to +127/−128 instead of wrapping. `sat` is `'1'` when clamping occurred.

## Ports

```vhdl
entity top_module is
  port (
    a, b : in  std_logic_vector(7 downto 0);
    s    : out std_logic_vector(7 downto 0);
    sat  : out std_logic
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

9-bit intermediate, then three cases: above 127, below −128, or in range.

</details>

## Check

```
./check.py 6.14
```
