# 8.9 byte_enable_reg

**New concept:** partial updates of a register; active-low reset.

Slices of a register can be updated independently: a slice assignment only
changes those bits, and the rest hold.

```vhdl
if wr_hi = '1' then word(15 downto 8) <= din(15 downto 8); end if;
```

Active-low signals conventionally end in `_n` or `n`; test them against `'0'`.

**Coming from Verilog:** `if (!resetn)` becomes `if resetn = '0' then`.

## Task

16-bit register `q`. `be(1)` enables writing the upper byte from `d(15 downto 8)`,
and `be(0)` the lower byte from `d(7 downto 0)`. Synchronous **active-low** reset
`resetn` clears `q` to 0.

## Ports

```vhdl
entity top_module is
  port (
    clk, resetn : in  std_logic;
    be          : in  std_logic_vector(1 downto 0);
    d           : in  std_logic_vector(15 downto 0);
    q           : out std_logic_vector(15 downto 0)
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

Two independent `if`s inside the `else` branch of the reset.

</details>

## Check

```
./check.py 8.9
```
