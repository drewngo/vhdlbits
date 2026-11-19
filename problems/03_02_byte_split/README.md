# 3.2 byte_split

**New concept:** slices `x(15 downto 8)`.

A slice is a contiguous sub-range of a vector. The slice direction must match the
declaration (`downto` for a `downto` vector).

```vhdl
opcode <= word(31 downto 26);
```

**Coming from Verilog:** `x[15:8]` becomes `x(15 downto 8)`. Writing `x(8 to 15)` on a `downto` vector is a null slice, not a reversal.

## Task

Split the 16-bit `din` into its upper byte `hi` and lower byte `lo`.

![din(15 downto 8) is hi, din(7 downto 0) is lo](diagram.svg)

## Ports

```vhdl
entity top_module is
  port (
    din    : in  std_logic_vector(15 downto 0);
    hi, lo : out std_logic_vector(7 downto 0)
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

Two slice assignments.

</details>

## Check

```
./check.py 3.2
```
