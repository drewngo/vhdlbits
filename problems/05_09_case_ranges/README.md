# 5.9 case_ranges

**New concept:** `case` on an integer with ranges (`when 48 to 57 =>`).

`case` choices on an integer can be ranges:

```vhdl
case to_integer(unsigned(temp)) is
  when 0 to 15  => band <= "00";
  when 16 to 30 => band <= "01";
  when others   => band <= "11";
end case;
```

`to_integer(unsigned(...))` comes from `ieee.numeric_std`, which Section 6 covers
properly. The stub already has `use ieee.numeric_std.all;`.

**Coming from Verilog:** Verilog `case` can't do ranges directly. Here the range is a single choice.

## Task

Classify the ASCII byte `ch`:

| `cls` | class |
|---|---|
| `"01"` | digit `'0'`–`'9'` (48–57) |
| `"10"` | uppercase letter `'A'`–`'Z'` (65–90) |
| `"11"` | lowercase letter `'a'`–`'z'` (97–122) |
| `"00"` | anything else |

## Ports

```vhdl
entity top_module is
  port (
    ch  : in  std_logic_vector(7 downto 0);
    cls : out std_logic_vector(1 downto 0)
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

`case to_integer(unsigned(ch)) is` with three ranges and `when others`.

</details>

## Check

```
./check.py 5.9
```
