# 7.14 truth_table3

**New concept:** implementing from a table.

When a function is given as a table, a `case` on the concatenated inputs is a
direct translation. To `case` on several signals, concatenate them into a
variable or signal first; VHDL-2008 also allows a qualified expression:

```vhdl
case std_logic_vector'(x & z) is
  when "00" => ...
```

**Coming from Verilog:** `case ({a,b,c})` needs a typed vector in VHDL: qualify the concatenation or use a helper signal.

## Task

Implement this truth table:

| a | b | c | y |
|---|---|---|---|
| 0 | 0 | 0 | 1 |
| 0 | 0 | 1 | 0 |
| 0 | 1 | 0 | 1 |
| 0 | 1 | 1 | 1 |
| 1 | 0 | 0 | 0 |
| 1 | 0 | 1 | 0 |
| 1 | 1 | 0 | 1 |
| 1 | 1 | 1 | 0 |

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

Either a `case` on `a & b & c`, or minimize and write the gates.

</details>

## Check

```
./check.py 7.14
```
