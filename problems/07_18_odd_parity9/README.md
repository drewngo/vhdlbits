# 7.18 odd_parity9

**New concept:** generating and checking a parity bit.

With **odd** parity, the parity bit is chosen so that the data bits plus the
parity bit contain an odd number of 1s. A receiver checks the whole word: an even
count means a bit flipped somewhere.

**Coming from Verilog:** `~^data` is `not (xor data)` (VHDL-2008 also has `xnor data`).

## Task

- `pbit`: the odd-parity bit for the 8 data bits in `data`
- `err`: `'1'` when the 9-bit received `word` (data plus parity) does **not** have odd parity

## Ports

```vhdl
entity top_module is
  port (
    data      : in  std_logic_vector(7 downto 0);
    word      : in  std_logic_vector(8 downto 0);
    pbit, err : out std_logic
  );
end entity top_module;
```

## Hints

<details><summary>Hint 1</summary>

Both outputs are a reduction plus possibly a `not`.

</details>

## Check

```
./check.py 7.18
```
