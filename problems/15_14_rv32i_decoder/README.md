# 15.14 rv32i_decoder

**New concept:** the main control decoder of a single-cycle CPU.

The control decoder turns an opcode into the datapath's control signals. A table
is the specification; a `case` on the opcode with default assignments is the
implementation.

**Coming from Verilog:** Same.

## Task

Decode `instr` (opcode = `instr(6 downto 0)`, `funct3 = instr(14 downto 12)`,
`funct7_5 = instr(30)`):

| opcode | reg_write | alu_src | mem_read | mem_write | mem_to_reg | branch | jump | alu_ctrl |
|---|---|---|---|---|---|---|---|---|
| `0110011` R-type | 1 | 0 | 0 | 0 | 0 | 0 | 0 | `funct7_5 & funct3` |
| `0010011` op-imm | 1 | 1 | 0 | 0 | 0 | 0 | 0 | `funct7_5 & funct3` if `funct3 = 101`, else `'0' & funct3` |
| `0000011` load | 1 | 1 | 1 | 0 | 1 | 0 | 0 | `0000` |
| `0100011` store | 0 | 1 | 0 | 1 | 0 | 0 | 0 | `0000` |
| `1100011` branch | 0 | 0 | 0 | 0 | 0 | 1 | 0 | `1000` |
| `1101111` jal | 1 | 0 | 0 | 0 | 0 | 0 | 1 | `0000` |
| `1100111` jalr | 1 | 1 | 0 | 0 | 0 | 0 | 1 | `0000` |
| `0110111` lui | 1 | 1 | 0 | 0 | 0 | 0 | 0 | `0000` |
| `0010111` auipc | 1 | 1 | 0 | 0 | 0 | 0 | 0 | `0000` |
| anything else | 0 | 0 | 0 | 0 | 0 | 0 | 0 | `0000` |

`alu_ctrl` uses the 15.12 encoding (`funct7_5 & funct3`).

## Ports

```vhdl
entity top_module is
  port (
    instr                                                             : in  std_logic_vector(31 downto 0);
    reg_write, alu_src, mem_read, mem_write, mem_to_reg, branch, jump : out std_logic;
    alu_ctrl                                                          : out std_logic_vector(3 downto 0)
  );
end entity top_module;
```

The grader biases `instr` toward valid RV32I opcodes.

## Hints

<details><summary>Hint 1</summary>

Default every output to `'0'`/`"0000"`, then a `case` on the opcode.

</details>

## Check

```
./check.py 15.14
```
