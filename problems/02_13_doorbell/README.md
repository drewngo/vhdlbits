# 2.13 doorbell

**New concept:** translating a word problem into logic.

Word problems become logic once you name every condition. Write down, for each
output, the exact situations in which it is `'1'`, then translate *and*/*or*/*not*
literally.

**Coming from Verilog:** Nothing new; just `and`/`not` with parentheses.

## Task

A doorbell has a `press` button input and a `mute` switch.

- When the button is pressed and `mute = '0'`, sound the chime (`chime = '1'`).
- When the button is pressed and `mute = '1'`, flash the light (`light = '1'`) instead.
- Never drive both outputs at once.

## Ports

```vhdl
entity top_module is
  port (
    press, mute  : in  std_logic;
    chime, light : out std_logic
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

Each output is the AND of `press` with `mute` or its inverse.

</details>

## Check

```
./check.py 2.13
```
