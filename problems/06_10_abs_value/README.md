# 6.10 abs_value

**New concept:** the edge case at the most negative value.

`abs` is defined for `signed`, but the result has the same width as the input, and
+128 doesn't fit in 8 signed bits: `abs(signed'(x"80"))` is `x"80"` again (−128).
Read as an **unsigned** number, though, those bits are 128, which is the right answer.

So computing the magnitude as `unsigned(abs(x))` works for every input. Checking
the edge case is a habit worth building whenever you negate.

**Coming from Verilog:** Same wraparound as Verilog's `-x` on 8 bits.

## Task

`a` is 8-bit signed. Output `mag = |a|` as an 8-bit **unsigned** value (so −128 gives 128), and `neg` = `'1'` when `a` is negative.

## Ports

```vhdl
entity top_module is
  port (
    a   : in  std_logic_vector(7 downto 0);
    mag : out std_logic_vector(7 downto 0);
    neg : out std_logic
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

`std_logic_vector(abs(signed(a)))` already gives the right bits for −128.

</details>

## Check

```
./check.py 6.10
```
