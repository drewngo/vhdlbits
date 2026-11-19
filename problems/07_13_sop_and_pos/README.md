# 7.13 sop_and_pos

**New concept:** two forms of the same function.

A **sum of products** (SOP) groups the 1s on a K-map; a **product of sums** (POS)
groups the 0s and writes each group as an OR term, then ANDs them. Both describe
the same function, and for some functions one form is much smaller than the other.

**Coming from Verilog:** Same exercise.

## Task

For `f = Σm(0, 2, 6, 7, 8, 10, 14, 15)` over `a b c d` (`a` = MSB), output the
minimal sum-of-products on `y_sop` and the minimal product-of-sums on `y_pos`.
Both are checked against `f`.

Write both forms by hand from the K-map before coding them.

## Ports

```vhdl
entity top_module is
  port (
    a, b, c, d   : in  std_logic;
    y_sop, y_pos : out std_logic
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

Notice that `a` doesn't matter at all.

</details>

<details><summary>Hint 2</summary>

Each minimal form has two terms.

</details>

## Check

```
./check.py 7.13
```
