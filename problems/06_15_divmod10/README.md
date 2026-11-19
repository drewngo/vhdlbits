# 6.15 divmod10

**New concept:** `/` and `mod` by a constant are synthesizable; by a variable they generally are not.

`numeric_std` defines `/`, `mod` and `rem` for `unsigned`. Synthesis tools turn
division by a **constant** into multiply-and-shift logic, and a power of two into
plain wiring. Division by a variable needs a real divider, which most tools refuse
to infer combinationally (see 15.11).

```vhdl
tens_digit <= resize(value / 10, 4);
```

**Coming from Verilog:** Same rule as Verilog synthesis: constant divisors only.

## Task

Output the quotient `q` and remainder `r` of the 8-bit unsigned `din` divided by 10.

## Ports

```vhdl
entity top_module is
  port (
    din : in  std_logic_vector(7 downto 0);
    q   : out std_logic_vector(4 downto 0);
    r   : out std_logic_vector(3 downto 0)
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

`unsigned(din) / 10` is 8 bits wide; `resize` it to 5 bits.

</details>

<details><summary>Hint 2</summary>

`unsigned(din) rem 10` is also 8 bits wide.

</details>

## Check

```
./check.py 6.15
```
