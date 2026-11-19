# 12.1 rom_const

**New concept:** a ROM as a `constant` array of `slv` indexed with `to_integer`.

A ROM is a constant array. Declare an array type, then a constant of that type,
and index it with an integer:

```vhdl
type sine_t is array (0 to 7) of std_logic_vector(7 downto 0);
constant SINE : sine_t := (x"80", x"DA", x"FF", x"DA", x"80", x"25", x"00", x"25");
...
sample <= SINE(to_integer(unsigned(phase)));
```

The contents can also be computed by a function at elaboration time, which beats
typing tables by hand.

**Coming from Verilog:** A `case` or an `initial` block filling a `reg` array. In VHDL the constant is part of the type system.

## Task

A 16×8 ROM whose word at address `a` is `a²` mod 256. The read is combinational: `data` shows the word at `addr`.

## Ports

```vhdl
entity top_module is
  port (
    addr : in  std_logic_vector(3 downto 0);
    data : out std_logic_vector(7 downto 0)
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

Either list the 16 values or write a function `init_rom return rom_t` with a loop.

</details>

<details><summary>Hint 2</summary>

15² = 225 still fits in a byte, so "mod 256" never actually wraps here.

</details>

## Check

```
./check.py 12.1
```
