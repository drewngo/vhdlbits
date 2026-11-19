# 7.6 kmap4

**New concept:** from truth table to minimal logic.

A Karnaugh map arranges a truth table so that adjacent cells differ in one input.
Groups of 1, 2, 4 or 8 adjacent 1s become single product terms. Rows and columns
are in Gray-code order, and the map wraps around at the edges.

Minimize by hand first, then write the expression. (Synthesis would minimize a
truth table for you, but reading K-maps is still a core skill, and a minimal
expression is easier to review.)

**Coming from Verilog:** Same exercise; just remember VHDL's parentheses rule.

## Task

`y = Σm(1, 3, 4, 5, 7, 9, 13, 15)` over inputs `a b c d` (`a` is the MSB of the
minterm number). The K-map, rows `ab`, columns `cd`:

| ab \ cd | 00 | 01 | 11 | 10 |
|---|---|---|---|---|
| **00** | 0 | 1 | 1 | 0 |
| **01** | 1 | 1 | 1 | 0 |
| **11** | 0 | 1 | 1 | 0 |
| **10** | 0 | 1 | 0 | 0 |

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

Look for a group of 4 in the column pattern first, then cover the stragglers.

</details>

<details><summary>Hint 2</summary>

Four product terms. Three of them are groups of four; the last covers just a pair.

</details>

## Check

```
./check.py 7.6
```
