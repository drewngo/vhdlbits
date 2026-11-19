# 7.12 kmap_dontcare

**New concept:** using don't-cares to simplify.

A **don't-care** is an input combination that never occurs (or whose output nobody
reads). On a K-map you may treat each one as 0 or 1, whichever makes bigger groups.

The grader skips the don't-care inputs, so any choice for them passes.

**Coming from Verilog:** Same exercise.

## Task

`y = Σm(2, 3, 5, 7, 11, 13) + d(0, 1, 15)` over `a b c d` (`a` = MSB).

| ab \ cd | 00 | 01 | 11 | 10 |
|---|---|---|---|---|
| **00** | x | x | 1 | 1 |
| **01** | 0 | 1 | 1 | 0 |
| **11** | 0 | 1 | x | 0 |
| **10** | 0 | 0 | 1 | 0 |

## Ports

```vhdl
entity top_module is
  port (
    a, b, c, d : in  std_logic;
    y          : out std_logic
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

Using 0, 1 and 15 as 1s gives groups of four.

</details>

<details><summary>Hint 2</summary>

Three product terms of two literals each.

</details>

## Check

```
./check.py 7.12
```
