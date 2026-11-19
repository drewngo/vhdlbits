# 3.17 rv_rtype_pack

**New concept:** concatenation to build a field-packed word.

Packing is the reverse of slicing: concatenate the fields in MSB-to-LSB order. The
R-type layout:

```
31     25 24  20 19  15 14  12 11   7 6      0
[ funct7 ][ rs2 ][ rs1 ][funct3][ rd ][ opcode ]
```

**Coming from Verilog:** `{funct7, rs2, rs1, funct3, rd, opcode}` becomes a chain of `&`.

## Task

Assemble the R-type instruction `instr` from `funct7`, `rs2`, `rs1`, `funct3`, `rd`, `opcode`.

![RISC-V R-type instruction fields](diagram.svg)

## Ports

```vhdl
entity top_module is
  port (
    funct7       : in  std_logic_vector(6 downto 0);
    rs2, rs1, rd : in  std_logic_vector(4 downto 0);
    funct3       : in  std_logic_vector(2 downto 0);
    opcode       : in  std_logic_vector(6 downto 0);
    instr        : out std_logic_vector(31 downto 0)
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

7 + 5 + 5 + 3 + 5 + 7 = 32.

</details>

## Check

```
./check.py 3.17
```
