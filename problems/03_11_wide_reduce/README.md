# 3.11 wide_reduce

**New concept:** reductions on long vectors.

Unary reductions work on any width, so a 100-input gate is still one line.
Synthesis builds a tree of smaller gates for you.

**Coming from Verilog:** Same as `&din`, `|din`, `^din`.

## Task

Output the AND, OR and XOR reductions of the 100-bit `din` on `r_and`, `r_or`, `r_xor`.

## Ports

```vhdl
entity top_module is
  port (
    din                : in  std_logic_vector(99 downto 0);
    r_and, r_or, r_xor : out std_logic
  );
end entity top_module;
```

The grader biases `din` toward all-ones so that `r_and` actually gets exercised.

## Hints

<details><summary>Hint 1</summary>

Three one-liners.

</details>

## Check

```
./check.py 3.11
```
