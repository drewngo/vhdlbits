# 7.10 mux9_default

**New concept:** `when others` producing a non-zero default.

`when others` doesn't have to output zero. Here it covers seven unused select
codes at once.

`(others => '1')` is a convenient all-ones value whose width comes from the target.

**Coming from Verilog:** `default: y = '1;` (SystemVerilog fill) becomes `when others => y <= (others => '1');`.

## Task

A 9-to-1 mux of 16-bit inputs (`sel` 0–8 picks `d0`–`d8`). For `sel` 9–15, output all ones.

## Ports

```vhdl
entity top_module is
  port (
    sel                                : in  std_logic_vector(3 downto 0);
    d0, d1, d2, d3, d4, d5, d6, d7, d8 : in  std_logic_vector(15 downto 0);
    y                                  : out std_logic_vector(15 downto 0)
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

A `case` with nine choices plus `when others`.

</details>

## Check

```
./check.py 7.10
```
