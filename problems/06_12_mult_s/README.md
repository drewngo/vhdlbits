# 6.12 mult_s

**New concept:** signed multiplication.

`signed * signed` also returns the combined width, and handles the signs for you.
Don't multiply as `unsigned` and fix up afterward.

**Coming from Verilog:** `$signed(a) * $signed(b)` is `signed(a) * signed(b)`.

## Task

Multiply the 8-bit signed `a` and `b` into the 16-bit signed product `p`.

## Ports

```vhdl
entity top_module is
  port (
    a, b : in  std_logic_vector(7 downto 0);
    p    : out std_logic_vector(15 downto 0)
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

Same as 6.11 with `signed`.

</details>

## Check

```
./check.py 6.12
```
