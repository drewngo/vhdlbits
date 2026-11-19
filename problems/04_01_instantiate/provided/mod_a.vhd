library ieee;
use ieee.std_logic_1164.all;

-- Provided: do not edit. o = in1 AND NOT in2
entity mod_a is
  port (
    in1, in2 : in  std_logic;
    o        : out std_logic
  );
end entity mod_a;

architecture rtl of mod_a is
begin
  o <= in1 and not in2;
end architecture rtl;
