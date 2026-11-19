# 7.11 adder100_numeric

**New concept:** compare with 4.11. One line with `numeric_std` gives the same hardware.

Synthesis tools recognize `+` and build an adder using the FPGA's dedicated carry
chain, which is faster than a generic ripple of LUTs. A 100-bit add with
carry-in and carry-out is a single expression if you widen by one bit:

```vhdl
wide <= ('0' & unsigned(x)) + unsigned(z) + ci;    -- VHDL-2008: unsigned + std_logic
```

**Coming from Verilog:** `assign {cout, sum} = a + b + cin;` maps to a 101-bit `unsigned` sum.

## Task

100-bit add with carry-in and carry-out: `{cout, sum} = a + b + cin`.

## Ports

```vhdl
entity top_module is
  port (
    a, b : in  std_logic_vector(99 downto 0);
    cin  : in  std_logic;
    sum  : out std_logic_vector(99 downto 0);
    cout : out std_logic
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

A 101-bit intermediate signal, then slice it.

</details>

## Check

```
./check.py 7.11
```
