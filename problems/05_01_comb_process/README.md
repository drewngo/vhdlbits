# 5.1 comb_process

**New concept:** `process(all)` (VHDL-2008) is the equivalent of `always @(*)`.

A **process** is a block of *sequential* statements (`if`, `case`, loops) that
re-runs whenever something in its sensitivity list changes. `process(all)` means
"every signal read inside", which is what you want for combinational logic.

```vhdl
process(all)
begin
  alarm <= smoke or heat;
end process;
```

The process as a whole is still one concurrent statement, side by side with
ordinary `<=` assignments in the architecture.

**Coming from Verilog:** `always @(*)` becomes `process(all)`, and `begin ... end` becomes `begin ... end process;`. Inside a process, `<=` is still the signal assignment.

## Task

Compute `a AND b` twice: once as a concurrent assignment (`y_conc`) and once inside a `process(all)` (`y_proc`).

## Ports

```vhdl
entity top_module is
  port (
    a, b           : in  std_logic;
    y_conc, y_proc : out std_logic
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

The process body is a single line, the same as the concurrent one.

</details>

## Check

```
./check.py 5.1
```
