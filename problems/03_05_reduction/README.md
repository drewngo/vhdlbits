# 3.5 reduction

**New concept:** VHDL-2008 unary reduction operators (`and v`, `or v`, `xor v`).

VHDL-2008 lets you put a logical operator in front of a single vector. It folds the
operator across every bit and returns one `std_logic`:

```vhdl
all_ready <= and ready_vec;   -- '1' only if every bit is '1'
```

Before 2008 you needed a loop or a function for this.

**Coming from Verilog:** `&v`, `|v`, `^v` become `and v`, `or v`, `xor v`.

## Task

- `all_ones` is `'1'` when every bit of `v` is set
- `any_one` is `'1'` when at least one bit is set
- `parity` is the XOR of all bits (even parity)

## Ports

```vhdl
entity top_module is
  port (
    v                         : in  std_logic_vector(7 downto 0);
    all_ones, any_one, parity : out std_logic
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

Three one-liners with unary `and`, `or`, `xor`.

</details>

## Check

```
./check.py 3.5
```
