# 5.11 last_assignment_wins

**New concept:** in a process, only the last signal assignment in a pass takes effect.

A signal can be assigned several times in one pass of a process. Only the last
assignment executed counts, because each one just overwrites the scheduled value.

```vhdl
process(all)
begin
  mode <= "00";
  if test = '1' then mode <= "11"; end if;   -- overrides the default
end process;
```

**Coming from Verilog:** Same as several nonblocking assignments to one reg in an `always` block.

## Task

`y` starts as `"00"`. Then: if `a = '1'`, set `y = "01"`; then if `b = '1'`, set
`y = "10"`; then if `a = '1'` and `b = '1'`, set `y = "11"`. Write it as three
separate `if`s, not `elsif`.

## Ports

```vhdl
entity top_module is
  port (
    a, b : in  std_logic;
    y    : out std_logic_vector(1 downto 0)
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

Four assignments in a row: one default and three guarded ones.

</details>

## Check

```
./check.py 5.11
```
