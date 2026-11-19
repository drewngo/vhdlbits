# 1.2 zero

**New concept:** a design with only an output.

An entity doesn't need inputs. Constant drivers like this show up as tie-offs:
unused enables pulled low, unused chip selects pulled high, and so on.

```vhdl
spare_cs_n <= '1';   -- park an unused active-low chip select
```

**Coming from Verilog:** Same as before: no `1'b0`, no `assign`.

## Task

Drive the output `o` permanently low.

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

A low bit is `'0'`.

</details>

## Check

```
./check.py 1.2
```
