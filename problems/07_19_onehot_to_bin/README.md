# 7.19 onehot_to_bin

**New concept:** encoding with validity checking.

Converting one-hot back to binary is easy if the input is guaranteed one-hot. If
it isn't, check first: exactly one bit set means `v /= 0` and `v and (v - 1) = 0`
when you treat `v` as `unsigned`.

**Coming from Verilog:** Same bit trick; `v & (v-1)` becomes `v and (v - 1)` on `unsigned`.

## Task

Convert the one-hot 8-bit `oh` to its binary index `idx`. `valid = '0'` if `oh` is not exactly one-hot, and then `idx = 0`.

## Ports

```vhdl
entity top_module is
  port (
    oh    : in  std_logic_vector(7 downto 0);
    idx   : out std_logic_vector(2 downto 0);
    valid : out std_logic
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

A loop that counts set bits and remembers the last index works too.

</details>

## Check

```
./check.py 7.19
```
