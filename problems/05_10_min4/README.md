# 5.10 min4

**New concept:** intermediate values in a process.

Variables are handy for multi-step combinational calculations: each step builds on
the previous one without declaring a signal for every intermediate.

```vhdl
process(all)
  variable best : unsigned(7 downto 0);
begin
  best := unsigned(x);
  if unsigned(z) > best then best := unsigned(z); end if;
  biggest <= std_logic_vector(best);
end process;
```

`<` and `>` on `std_logic_vector` compare as *strings* of characters, which happens
to work for equal lengths but is a bad habit. Convert to `unsigned` first.

**Coming from Verilog:** Comparisons on `std_logic_vector` aren't numeric. Cast to `unsigned`.

## Task

Output on `m` the minimum of four 8-bit unsigned values `a`, `b`, `c`, `d`.

## Ports

```vhdl
entity top_module is
  port (
    a, b, c, d : in  std_logic_vector(7 downto 0);
    m          : out std_logic_vector(7 downto 0)
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

A variable holding the running minimum, updated three times.

</details>

## Check

```
./check.py 5.10
```
