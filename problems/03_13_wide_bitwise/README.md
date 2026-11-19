# 3.13 wide_bitwise

**New concept:** bitwise ops on wide vectors are a single line.

Bitwise operators on equal-length vectors produce a vector of the same length, so
the width of the operands doesn't change the code.

**Coming from Verilog:** Same as Verilog, with keyword operators.

## Task

For four 64-bit inputs: `all_and = a AND b AND c AND d`, `any_or` the same with OR, and `odd = a XOR b XOR c XOR d`.

## Ports

```vhdl
entity top_module is
  port (
    a, b, c, d           : in  std_logic_vector(63 downto 0);
    all_and, any_or, odd : out std_logic_vector(63 downto 0)
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

Three one-liners.

</details>

## Check

```
./check.py 3.13
```
