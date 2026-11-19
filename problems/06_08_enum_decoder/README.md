# 6.8 enum_decoder

**New concept:** user-defined enumerated `type` inside an architecture, then decoding it to outputs.

An **enumerated type** names its values. The tools choose the encoding.

```vhdl
type mode_t is (OFF, LOW, HIGH);
signal mode : mode_t;
...
case mode is
  when OFF  => fan <= "00";
  when LOW  => fan <= "01";
  when HIGH => fan <= "11";
end case;
```

A `case` on an enum needs no `when others` if every value is listed. That's a nice
property: add a value later and the compiler points to every `case` that forgot it.

**Coming from Verilog:** Instead of `localparam` codes, VHDL has real enumerated types. The simulator shows the names in the waveform.

## Task

Declare `type stage_t is (IDLE, LOAD, RUN, DONE)` in the architecture. Decode `sel`
into a `stage_t` signal (0 → IDLE … 3 → DONE). Then drive the outputs from the
enum with a `case`: `busy` is `'1'` in LOAD or RUN, and `fin` is `'1'` in DONE.

## Ports

```vhdl
entity top_module is
  port (
    sel       : in  std_logic_vector(1 downto 0);
    busy, fin : out std_logic
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

`stage_t'val(to_integer(unsigned(sel)))` converts an integer position to the enum value, or use a `case` on `sel`.

</details>

<details><summary>Hint 2</summary>

`when LOAD | RUN =>` groups two values.

</details>

## Check

```
./check.py 6.8
```
