library ieee;
use ieee.std_logic_1164.all;

-- Provided: do not edit. o1 = w XOR x, o2 = y AND z
entity mod_b is
  port (
    w, x, y, z : in  std_logic;
    o1, o2     : out std_logic
  );
end entity mod_b;

architecture rtl of mod_b is
begin
  o1 <= w xor x;
  o2 <= y and z;
end architecture rtl;
