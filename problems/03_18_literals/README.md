# 3.18 literals

**New concept:** bit-string literals `x"A5"`, `b"1010"`, `o"17"`, and VHDL-2008 sized literals `12x"ABC"`.

Vector constants can be written in several bases:

| literal | bits |
|---|---|
| `"1010"` or `b"1010"` | binary, 4 bits |
| `x"A5"` | hex, 4 bits per digit = 8 bits |
| `o"17"` | octal, 3 bits per digit = 6 bits |
| `12x"ABC"` | VHDL-2008: hex digits, sized to 12 bits |
| `10x"0F"` | sized: zero-padded on the left to 10 bits |
| `x"1_0"` | underscores are ignored, for readability |

The literal's length must match whatever it's compared with or assigned to.
`(others => '1')` is the width-independent way to write all ones, but it can't be
used directly as a comparison operand because its width is unknown there.

**Coming from Verilog:** `8'hA5` becomes `x"A5"`, and `12'hABC` becomes `12x"ABC"`.

## Task

- `is_zero`: `din` equals 0
- `is_a5`: `din` equals `x"A5"`
- `is_max`: `din` is all ones
- `masked` = `din AND x"0F"`

## Ports

```vhdl
entity top_module is
  port (
    din                    : in  std_logic_vector(7 downto 0);
    is_zero, is_a5, is_max : out std_logic;
    masked                 : out std_logic_vector(7 downto 0)
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

Each flag is a `'1' when ... else '0'` conditional assignment.

</details>

<details><summary>Hint 2</summary>

For all ones, `x"FF"` works here; `and din` (3.5) is a width-independent alternative.

</details>

## Check

```
./check.py 3.18
```
