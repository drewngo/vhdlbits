# 6.4 popcount

**New concept:** a `variable` counter inside a combinational process with a `for` loop.

A variable can be an `integer` or `unsigned` counter that a loop increments. Each
iteration becomes an adder stage in hardware.

```vhdl
process(all)
  variable n : unsigned(2 downto 0);
begin
  n := (others => '0');
  for i in flags'range loop
    if flags(i) = '1' then n := n + 1; end if;
  end loop;
  num_flags <= std_logic_vector(n);
end process;
```

`unsigned + integer` is defined in `numeric_std`, so `n + 1` works.

**Coming from Verilog:** Same as a `for` loop in `always @(*)` with a blocking counter.

## Task

Output on `count` the number of `'1'` bits in `din`.

## Ports

```vhdl
entity top_module is
  port (
    din   : in  std_logic_vector(7 downto 0);
    count : out std_logic_vector(3 downto 0)
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

A 4-bit variable is enough: the count is at most 8.

</details>

## Check

```
./check.py 6.4
```
