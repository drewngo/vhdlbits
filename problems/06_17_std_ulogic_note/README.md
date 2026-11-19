# 6.17 std_ulogic_note

**New concept:** `std_ulogic` (unresolved) vs. `std_logic`, and multiple-driver errors caught at compile time.

`std_logic` is a *resolved* subtype of `std_ulogic`: when a signal has several
drivers, a resolution function combines them (that's how `'Z'` buses work).
`std_ulogic` is the same nine values **without** resolution, so a second driver is
an error at elaboration instead of an `'X'` you find in the waveform hours later.

```vhdl
signal en : std_ulogic;
en <= a;
en <= b;     -- error: several sources for unresolved signal "en"
```

Many style guides (and the VHDL-2008 standard library) prefer `std_ulogic` and
`std_ulogic_vector` for everything except real tri-state buses. They mix freely
with `std_logic`, since in VHDL-2008 `std_logic_vector` is a subtype of
`std_ulogic_vector`.

**Coming from Verilog:** Verilog `wire` resolves multiple drivers silently. `std_ulogic` is closer to SystemVerilog's single-driver `logic` checks.

## Task

The stub uses `std_ulogic` ports and already contains a leftover driver for `y`.
Implement `y = a OR b` with a concurrent assignment and try to compile: GHDL
will report the second driver. Remove the leftover so `y` has exactly one.

## Ports

```vhdl
entity top_module is
  port (
    a, b : in  std_ulogic;
    y    : out std_ulogic
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

A process that assigns a signal is a driver of it, whatever the assigned value.

</details>

## Check

```
./check.py 6.17
```
