# 1.1 one

**New concept:** entity + architecture, concurrent assignment, character literals.

A VHDL design comes in two parts. The **entity** is the interface: its name and
its ports. The **architecture** is the body: what the design does. Statements between
`begin` and `end architecture` run concurrently, all the time, like wires.

```vhdl
entity leds_off is
  port (led : out std_logic_vector(3 downto 0));
end entity leds_off;

architecture rtl of leds_off is
begin
  led <= "0000";      -- a vector literal uses double quotes
end architecture rtl;
```

`<=` is the signal assignment operator. A single bit is a *character literal*
in single quotes: `'0'` or `'1'`.

**Coming from Verilog:** `1'b1` is a syntax error. A single bit is written `'1'`, and there is no `assign` keyword.

## Task

Drive the output `o` permanently high.

## Ports

```vhdl
entity top_module is
  port (
    o : out std_logic
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

One line between `begin` and `end architecture`: `o <= ...;`

</details>

## Check

```
./check.py 1.1
```
