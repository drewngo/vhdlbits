# 7.21 thermometer

**New concept:** thermometer code (common in ADC/flash designs).

A **thermometer code** sets the lowest `n` bits of a vector, like mercury rising.
Flash ADCs produce it naturally from a row of comparators.

**Coming from Verilog:** Nothing new; a loop or a lookup.

## Task

Convert the 3-bit value `n` to a 7-bit output `t` with the lowest `n` bits set (`n = 0` gives `"0000000"`, `n = 7` gives `"1111111"`).

## Ports

```vhdl
entity top_module is
  port (
    n : in  std_logic_vector(2 downto 0);
    t : out std_logic_vector(6 downto 0)
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

`t(i) <= '1' when i < to_integer(unsigned(n)) else '0';` in a generate.

</details>

## Check

```
./check.py 7.21
```
