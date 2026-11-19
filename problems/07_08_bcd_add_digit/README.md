# 7.8 bcd_add_digit

**New concept:** add-6 correction.

Adding two BCD digits in binary gives 0–19. Results above 9 aren't valid BCD:
adding 6 skips the six unused codes (`1010`–`1111`), wrapping the digit into
range and producing a decimal carry.

```
  7 + 5 = 12 = 0b01100 → too big → 12 + 6 = 18 = 0b1_0010 → digit 2, carry 1
```

**Coming from Verilog:** Same arithmetic; widen to 5 bits before adding.

## Task

Add two BCD digits `a`, `b` and the carry-in `cin` (inputs are always valid BCD 0–9). Output the BCD digit `s` and carry-out `cout`.

## Ports

```vhdl
entity top_module is
  port (
    a, b : in  std_logic_vector(3 downto 0);
    cin  : in  std_logic;
    s    : out std_logic_vector(3 downto 0);
    cout : out std_logic
  );
end entity top_module;
```

The grader only drives 0–9 on `a` and `b`.

## Hints

<details><summary>Hint 1</summary>

5-bit binary sum; if it's above 9, add 6 and set `cout`.

</details>

## Check

```
./check.py 7.8
```
