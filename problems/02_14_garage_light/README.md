# 2.14 garage_light

**New concept:** combining conditions with an override.

An override that forces an output off is an AND with the override's inverse,
applied last:

```vhdl
heater <= (cold and occupied) and not window_open;
```

**Coming from Verilog:** Precedence again: write every grouping explicitly.

## Task

The `light` turns on when the door is open, or when motion is detected while it's
dark. A `force_off` override turns it off regardless.

## Ports

```vhdl
entity top_module is
  port (
    door_open, motion, dark, force_off : in  std_logic;
    light                              : out std_logic
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

`(door_open or (motion and dark)) and not force_off`

</details>

## Check

```
./check.py 2.14
```
