# 16.2 bug_latch

**New concept:** debugging a combinational decoder.

This file is a complete design that compiles, but it has a bug. The task below says what
the design is **supposed** to do. Find the bug with the grader and the waveform, and fix
it, changing as little as possible.

**Coming from Verilog:** Bugs like this one exist in Verilog too; the VHDL symptoms are what's worth learning to recognize.

## Task

Decode a 4-bit opcode into control lines. Every output is `'0'` unless listed:

| op | asserted outputs |
|---|---|
| `0001` | `alu_en` |
| `0010` | `alu_en`, `wr_reg` |
| `0100` | `mem_rd`, `wr_reg` |
| `0101` | `mem_wr` |
| `1000` | `branch` |
| `1111` | `halt` |
| anything else | none |

## Ports

```vhdl
entity top_module is
  port (
    op                                           : in  std_logic_vector(3 downto 0);
    alu_en, wr_reg, mem_rd, mem_wr, branch, halt : out std_logic
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

After `op = "0001"`, what is `alu_en` when `op` changes to `"0000"`?

</details>

## Check

```
./check.py 16.2
```
