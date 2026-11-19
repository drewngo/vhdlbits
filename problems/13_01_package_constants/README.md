# 13.1 package_constants

**New concept:** a `package` with constants, and `use work.my_pkg.all`.

A **package** collects declarations (constants, types, functions) that several
design units share. It lives in its own file and is compiled into a library before
anything that uses it:

```vhdl
package bus_pkg is
  constant ADDR_BITS : positive := 16;
  constant RESET_VEC : std_logic_vector(15 downto 0) := x"FFF0";
end package bus_pkg;
```

A design then imports it with `use work.bus_pkg.all;` in its context clause.

This problem has more than one file you edit. The grader compiles every listed file,
packages (`*_pkg.vhd`) first, then `top_module.vhd`.

**Coming from Verilog:** Closest to a header of `` `define``s or a SystemVerilog `package`. VHDL packages are typed and scoped, not textual macros.

## Task

In `my_pkg.vhd`, declare `constant WIDTH : positive := 12` and
`constant MAGIC : std_logic_vector(11 downto 0) := x"5A3"`. In `top_module.vhd`
(which already has `use work.my_pkg.all;`), output `dout = din XOR MAGIC`.

## Ports

```vhdl
entity top_module is
  port (
    din  : in  std_logic_vector(11 downto 0);
    dout : out std_logic_vector(11 downto 0)
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

The constants go between `package my_pkg is` and `end package`.

</details>

## Check

```
./check.py 13.1
```
