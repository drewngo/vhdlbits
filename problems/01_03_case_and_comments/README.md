# 1.3 case_and_comments

**New concept:** VHDL is case-insensitive, comments start with `--`, and a statement ends with `;`.

`SIGNAL`, `Signal` and `signal` are the same keyword, and `Data_In` and `DATA_IN`
name the same object. Most code bases pick lowercase keywords and stick to it,
but you will see every style in vendor code.

```vhdl
-- this whole line is a comment
Ready <= '1';  -- and so is everything after the dashes here
```

VHDL-2008 also has block comments `/* ... */`, though `--` is far more common.

The stub below deliberately mixes casing. It still compiles: case only
matters inside character and string literals, where `'1'` and `"0Z"` mean
exactly what they say (and `'z'` is not the same character as `'Z'`).

**Coming from Verilog:** Verilog identifiers are case-sensitive, so `clk` and `CLK` are different nets. In VHDL they are the same name, and declaring both is a redeclaration error.

## Task

Output the input inverted: `y` is the logical NOT of `a`. Use the `not` keyword.

## Ports

```vhdl
ENTITY top_module IS
  PORT (
    a : IN  std_logic;
    y : OUT STD_LOGIC
  );
END ENTITY top_module;
```

## Hints

<details><summary>Hint 1</summary>

`y <= not a;` — and try writing it as `Y <= NOT A;` to see that it's the same thing.

</details>

## Check

```
./check.py 1.3
```
