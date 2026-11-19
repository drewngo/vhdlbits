# 15.12 rv32i_alu

**New concept:** a real ALU, bridge to the RISC-V core.

The RV32I integer ALU is selected by the instruction's `funct3` plus bit 5 of
`funct7` (which distinguishes ADD/SUB and SRL/SRA). Shift amounts use only the low
5 bits of `b`.

**Coming from Verilog:** Same; arithmetic shift right is `shift_right` on `signed`.

## Task

| `funct7_5` | `funct3` | operation |
|---|---|---|
| 0 | `000` | ADD: `a + b` |
| 1 | `000` | SUB: `a - b` |
| x | `001` | SLL: `a << b(4:0)` |
| x | `010` | SLT: 1 if `a < b` signed, else 0 |
| x | `011` | SLTU: 1 if `a < b` unsigned, else 0 |
| x | `100` | XOR |
| 0 | `101` | SRL: logical `a >> b(4:0)` |
| 1 | `101` | SRA: arithmetic `a >> b(4:0)` |
| x | `110` | OR |
| x | `111` | AND |

All results are 32 bits and wrap.

## Ports

```vhdl
entity top_module is
  port (
    a, b     : in  std_logic_vector(31 downto 0);
    funct3   : in  std_logic_vector(2 downto 0);
    funct7_5 : in  std_logic;
    y        : out std_logic_vector(31 downto 0)
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

A `case funct3 is` with `funct7_5` tested inside the `000` and `101` branches.

</details>

## Check

```
./check.py 15.12
```
