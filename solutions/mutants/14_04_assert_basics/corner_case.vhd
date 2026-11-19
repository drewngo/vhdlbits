library ieee;
use ieee.std_logic_1164.all;

-- Mutant: wrong only for a=1, b=0, sel=1.
entity mux2 is
  port (
    a, b, sel : in  std_logic;
    y         : out std_logic
  );
end entity mux2;

architecture rtl of mux2 is
begin
  y <= a when sel = '1' and a = '1' else b when sel = '1' else a;
end architecture rtl;
