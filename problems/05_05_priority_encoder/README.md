# 5.5 priority_encoder

**New concept:** VHDL-2008 matching case `case? ... is` with `'-'` don't-cares. This replaces Verilog's `casez`.

In a normal `case`, `'-'` is just another literal value. The VHDL-2008 **matching
case**, `case?`, treats `'-'` in a choice as "matches anything":

```vhdl
case? req is
  when "1--" => grant <= "100";
  when "01-" => grant <= "010";
  when "001" => grant <= "001";
  when others => grant <= "000";
end case?;
```

Choices are checked as a set, not in order, so they must not overlap. Write them
so that each input pattern matches exactly one choice.

**Coming from Verilog:** `casez` with `?` becomes `case?` with `'-'`. Unlike `casez`, overlapping choices are an error, not a priority list.

## Task

Output on `pos` the index of the **lowest** set bit of the 8-bit input `din`, or 0 if no bit is set.

## Ports

```vhdl
entity top_module is
  port (
    din : in  std_logic_vector(7 downto 0);
    pos : out std_logic_vector(2 downto 0)
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

Bit 0 set means `pos = 0` regardless of the others: `when "-------1" =>`.

</details>

<details><summary>Hint 2</summary>

The next choice is `"------10"`, and so on.

</details>

## Check

```
./check.py 5.5
```
