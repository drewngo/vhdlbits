# 7.20 alu4

**New concept:** a small ALU, the bridge to a CPU datapath.

An ALU is a mux in front of several function units. Compute the selected result in
a `case`, then derive flags from the result.

Comparison results are one bit, zero-extended to the ALU width, as in RISC-V
`slt`.

**Coming from Verilog:** Signed vs. unsigned comparisons are explicit casts here, not declarations.

## Task

4-bit ALU. Results wrap at 4 bits.

| `op` | `y` |
|---|---|
| `000` | `a + b` |
| `001` | `a - b` |
| `010` | `a and b` |
| `011` | `a or b` |
| `100` | `a xor b` |
| `101` | `"0001"` if `a < b` as **signed**, else `"0000"` |
| `110` | `"0001"` if `a < b` as **unsigned**, else `"0000"` |
| `111` | `b` |

`zero` is `'1'` when `y` is `"0000"`.

## Ports

```vhdl
entity top_module is
  port (
    a, b : in  std_logic_vector(3 downto 0);
    op   : in  std_logic_vector(2 downto 0);
    y    : out std_logic_vector(3 downto 0);
    zero : out std_logic
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

Compute `y` in a process with a variable, then `zero` from that variable (or from the output port, readable in VHDL-2008).

</details>

## Check

```
./check.py 7.20
```
