# 6.5 mux256

**New concept:** `to_integer(unsigned(sel))` as an array index.

Indices are integers. Convert a vector to an integer to use it as an index:

```vhdl
bit_out <= mask(to_integer(unsigned(addr)));
```

Synthesis turns a variable index into a mux.

**Coming from Verilog:** `din[sel]` needs `to_integer(unsigned(sel))` as the index.

## Task

Output on `y` the bit of `din` selected by `sel`: `y = din(sel)`.

## Ports

```vhdl
entity top_module is
  port (
    din : in  std_logic_vector(255 downto 0);
    sel : in  std_logic_vector(7 downto 0);
    y   : out std_logic
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

One line.

</details>

## Check

```
./check.py 6.5
```
