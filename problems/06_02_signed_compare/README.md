# 6.2 signed_compare

**New concept:** the same bits compare differently as `signed` vs. `unsigned`.

`x"FF"` is 255 as `unsigned` and −1 as `signed`. Comparisons use the type you
give them:

```vhdl
neg_bigger <= '1' when signed(p) > signed(q) else '0';
```

The result of a comparison is a `boolean`, so turn it into `std_logic` with
`when ... else`.

**Coming from Verilog:** In Verilog, a comparison is signed only if *both* operands are declared `signed`. In VHDL the operand types decide, and mixing `signed` with `unsigned` is a compile error.

## Task

Treat `a` and `b` as signed. Set flags `lt` (a < b), `eq`, and `gt`, and output
`min_s`, the signed minimum. Also output `lt_u`, an **unsigned** `a < b`, to show
the difference.

## Ports

```vhdl
entity top_module is
  port (
    a, b             : in  std_logic_vector(7 downto 0);
    lt, eq, gt, lt_u : out std_logic;
    min_s            : out std_logic_vector(7 downto 0)
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

`lt <= '1' when signed(a) < signed(b) else '0';`

</details>

## Check

```
./check.py 6.2
```
