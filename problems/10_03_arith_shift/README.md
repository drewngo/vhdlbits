# 10.3 arith_shift

**New concept:** `shift_right` on `signed` replicates the sign bit.

`shift_right(signed(x), n)` fills from the left with copies of the sign bit, which
divides by 2ⁿ rounding toward −∞. On `unsigned` it fills with zeros.

**Coming from Verilog:** `>>>` on a `signed` reg is `shift_right` on `signed`.

## Task

16-bit register `q`, no reset. On an edge with `load = '1'`, load `d`. Otherwise,
when `en = '1'`, `amt` selects:

| `amt` | operation |
|---|---|
| `00` | shift left by 1 |
| `01` | shift left by 4 |
| `10` | arithmetic shift right by 1 |
| `11` | arithmetic shift right by 4 |

## Ports

```vhdl
entity top_module is
  port (
    clk, load, en : in  std_logic;
    amt           : in  std_logic_vector(1 downto 0);
    d             : in  std_logic_vector(15 downto 0);
    q             : out std_logic_vector(15 downto 0)
  );
end entity top_module;
```

With no reset, the grader asserts `load` in the first cycle so the register starts from a known value.

## Hints

<details><summary>Hint 1</summary>

Keep the register as `signed`; `shift_left` and `shift_right` both work on it.

</details>

## Check

```
./check.py 10.3
```
