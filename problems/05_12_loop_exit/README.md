# 5.12 loop_exit

**New concept:** `for` loops with `exit`; loops describe hardware, not runtime iteration.

A `for` loop in a process unrolls at synthesis. `exit` leaves the loop early, and
the hardware it describes is a priority chain:

```vhdl
for i in 0 to 7 loop
  if err(i) = '1' then
    first_err := i;
    exit;
  end if;
end loop;
```

The loop index is an `integer`; `to_unsigned(i, width)` converts it to a vector.

**Coming from Verilog:** `break` in a SystemVerilog loop is `exit` in VHDL.

## Task

Output on `idx` the index of the **highest** set bit of the 16-bit `din`, and `valid = '1'` if any bit is set. Output `idx = 0` when none are set.

## Ports

```vhdl
entity top_module is
  port (
    din   : in  std_logic_vector(15 downto 0);
    idx   : out std_logic_vector(3 downto 0);
    valid : out std_logic
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

Loop `for i in 15 downto 0`, and `exit` on the first `'1'`.

</details>

<details><summary>Hint 2</summary>

Assign defaults (`idx <= "0000"; valid <= '0';`) before the loop.

</details>

## Check

```
./check.py 5.12
```
