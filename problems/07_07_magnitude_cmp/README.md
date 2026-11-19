# 7.7 magnitude_cmp

**New concept:** comparators from `numeric_std` vs. by hand.

With `numeric_std` a comparator is one line per flag. Try writing it both ways:
once with `unsigned` comparisons, and once by hand (an MSB-first chain: the first
bit position where the inputs differ decides).

**Coming from Verilog:** `a > b` on vectors is numeric in Verilog; in VHDL, cast to `unsigned` first.

## Task

Compare the 4-bit unsigned `a` and `b`: `gt`, `eq`, `lt`.

## Ports

```vhdl
entity top_module is
  port (
    a, b       : in  std_logic_vector(3 downto 0);
    gt, eq, lt : out std_logic
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

Exactly one of the three outputs is `'1'` at a time.

</details>

## Check

```
./check.py 7.7
```
