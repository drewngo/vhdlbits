# 2.9 all_gates

**New concept:** many outputs from the same two inputs.

Each output is its own concurrent statement. This is a good moment to get used to
`nand`, `nor` and `xnor` as operators.

```vhdl
differ <= p xor q;
```

**Coming from Verilog:** `a & ~b` becomes `a and not b`.

## Task

From `a` and `b`, produce `o_and`, `o_or`, `o_xor`, `o_nand`, `o_nor`, `o_xnor`, and
`o_andnot` (`a AND NOT b`).

## Ports

```vhdl
entity top_module is
  port (
    a, b                                                : in  std_logic;
    o_and, o_or, o_xor, o_nand, o_nor, o_xnor, o_andnot : out std_logic
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

Seven one-liners. `not` binds tighter than `and`, so `a and not b` needs no parentheses.

</details>

## Check

```
./check.py 2.9
```
