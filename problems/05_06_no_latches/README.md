# 5.6 no_latches

**New concept:** default assignments at the top of a combinational process, so incomplete branches can't infer latches.

In a combinational process, every output must be assigned on every path. If some
path skips an output, the process has to *remember* its old value, and synthesis
infers a latch.

The clean fix is to assign defaults first and override them in the branches.
Within one pass of a process the last assignment wins, so this is safe:

```vhdl
process(all)
begin
  buzz  <= '0';
  flash <= '0';
  if alarm = '1' then
    buzz <= '1';
  end if;
end process;
```

**Coming from Verilog:** Same rule as `always @(*)`: assign everything on every path. Defaults at the top are the usual idiom in both languages.

## Task

Decode a 4-bit opcode into control lines. Every output defaults to `'0'`.

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

Six default assignments, then a `case op is` whose `when others => null;` is now safe.

</details>

## Check

```
./check.py 5.6
```
