# 7.4 decoder3to8

**New concept:** one-hot output with enable.

A decoder turns a binary index into a one-hot vector. With `numeric_std`, you can
set one bit at an integer position:

```vhdl
process(all)
begin
  sel_lines <= (others => '0');
  sel_lines(to_integer(unsigned(idx))) <= '1';
end process;
```

Assigning an element after the whole vector is fine: last assignment wins per bit.

**Coming from Verilog:** `y = en << a` doesn't translate directly; build the vector explicitly.

## Task

When `en = '1'`, set exactly one bit of `y`: `y(i) = '1'` for input `a = i`. When `en = '0'`, all bits are `'0'`.

## Ports

```vhdl
entity top_module is
  port (
    a  : in  std_logic_vector(2 downto 0);
    en : in  std_logic;
    y  : out std_logic_vector(7 downto 0)
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

Default all zeros, then set one bit inside `if en = '1'`.

</details>

## Check

```
./check.py 7.4
```
