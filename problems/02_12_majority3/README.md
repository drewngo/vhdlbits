# 2.12 majority3

**New concept:** sum-of-products for a voting function.

A majority voter is common in fault-tolerant designs (triple modular redundancy).
Write the output as a sum of products: one term per pair of inputs.

**Coming from Verilog:** `(a&b)|(b&c)|(a&c)` needs explicit parentheses around every product.

## Task

`y` is `'1'` when at least two of the three inputs are `'1'`.

## Ports

```vhdl
entity top_module is
  port (
    a, b, c : in  std_logic;
    y       : out std_logic
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

Three AND terms ORed together.

</details>

## Check

```
./check.py 2.12
```
