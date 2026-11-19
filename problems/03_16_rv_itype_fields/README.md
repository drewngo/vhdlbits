# 3.16 rv_itype_fields

**New concept:** slicing a real instruction format.

RISC-V instructions are fixed 32-bit words with fields at fixed positions. Decoding
them is pure slicing. The I-type format:

```
31        20 19   15 14  12 11    7 6      0
[ imm[11:0] ][ rs1  ][funct3][  rd  ][ opcode ]
```

The immediate is a 12-bit two's-complement value and is sign-extended to 32 bits.

**Coming from Verilog:** Same field extraction, with `downto` slices and aggregate-based sign extension.

## Task

Split the I-type instruction `instr` into `opcode` [6:0], `rd` [11:7], `funct3`
[14:12], `rs1` [19:15], and `imm`, which is bits [31:20] sign-extended to 32 bits.

![RISC-V I-type instruction fields](diagram.svg)

## Ports

```vhdl
entity top_module is
  port (
    instr   : in  std_logic_vector(31 downto 0);
    opcode  : out std_logic_vector(6 downto 0);
    rd, rs1 : out std_logic_vector(4 downto 0);
    funct3  : out std_logic_vector(2 downto 0);
    imm     : out std_logic_vector(31 downto 0)
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

`imm <= (19 downto 0 => instr(31)) & instr(31 downto 20);`

</details>

## Check

```
./check.py 3.16
```
