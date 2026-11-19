# 3.4 bitwise_vs_logical

**New concept:** VHDL has no `||`. Logical tests produce `boolean`, which you have to convert to `std_logic`.

`and`/`or` on vectors are **bitwise**: they work element by element and return a
vector. A *test* such as `v /= "000"` returns a `boolean` (`true`/`false`), which is a
different type from `std_logic`. You can't assign a `boolean` to a `std_logic`
signal directly; convert it with a conditional assignment:

```vhdl
nonempty <= '1' when count /= "0000" else '0';
```

Booleans can be combined with `and`/`or` too: `(x /= "00") or (z = "11")` is a
boolean.

**Coming from Verilog:** `a || b` on vectors means "either is nonzero". In VHDL write the test explicitly: `(a /= "000") or (b /= "000")`, then turn the boolean into `'1'`/`'0'`.

## Task

- `or_bitwise` = bitwise OR of `a` and `b`
- `or_logical` = `'1'` if either vector is nonzero
- `not_both` = bitwise NOT of `b` in the upper 3 bits and bitwise NOT of `a` in the lower 3 bits

## Ports

```vhdl
entity top_module is
  port (
    a, b       : in  std_logic_vector(2 downto 0);
    or_bitwise : out std_logic_vector(2 downto 0);
    or_logical : out std_logic;
    not_both   : out std_logic_vector(5 downto 0)
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

`not` works on whole vectors, and `&` concatenates them.

</details>

<details><summary>Hint 2</summary>

`or_logical <= '1' when (a /= "000") or (b /= "000") else '0';`

</details>

## Check

```
./check.py 3.4
```
