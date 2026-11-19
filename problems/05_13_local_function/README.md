# 5.13 local_function

**New concept:** declaring a `function` in the architecture's declarative region.

A function computes a value from its parameters. It can be declared where signals
are, before `begin`. Parameters can be **unconstrained**, so one function handles
any width:

```vhdl
function ones(v : std_logic_vector) return natural is
  variable n : natural := 0;
begin
  for i in v'range loop
    if v(i) = '1' then n := n + 1; end if;
  end loop;
  return n;
end function;
```

Use `v'range` inside, never fixed indices; a slice passed in might be
`(15 downto 8)`.

**Coming from Verilog:** Like a Verilog `function`, but parameters can be unconstrained arrays.

## Task

Write `function parity(v: std_logic_vector) return std_logic` that returns the XOR
of all bits of `v`. Use it on both inputs: `pa = parity(a)`, `pb = parity(b)`.

## Ports

```vhdl
entity top_module is
  port (
    a      : in  std_logic_vector(7 downto 0);
    b      : in  std_logic_vector(15 downto 0);
    pa, pb : out std_logic
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

A variable accumulator and `for i in v'range loop`. (`xor v` also works inside the function.)

</details>

## Check

```
./check.py 5.13
```
