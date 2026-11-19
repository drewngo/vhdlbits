# 6.16 bin_to_bcd

**New concept:** the double-dabble algorithm as a loop with a variable.

**Double dabble** converts binary to BCD with shifts and small additions. Keep a
scratch register made of the BCD digits followed by the binary input. Repeat once
per input bit:

1. For every BCD digit that is 5 or more, add 3 to it.
2. Shift the whole scratch register left by one.

After the last shift the BCD digits hold the answer. In a combinational process
this is a `for` loop over a variable, which unrolls into a fixed network of
small adders.

**Coming from Verilog:** Same as a `for` loop with blocking assignments in `always @(*)`.

## Task

Convert the 8-bit binary `bin` into three BCD digits `hundreds`, `tens`, `ones`.

## Ports

```vhdl
entity top_module is
  port (
    bin                  : in  std_logic_vector(7 downto 0);
    hundreds, tens, ones : out std_logic_vector(3 downto 0)
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

Scratch register: `unsigned(19 downto 0)` = 12 BCD bits + 8 binary bits.

</details>

<details><summary>Hint 2</summary>

Do the add-3 checks *before* each shift, 8 iterations in total.

</details>

## Check

```
./check.py 6.16
```
