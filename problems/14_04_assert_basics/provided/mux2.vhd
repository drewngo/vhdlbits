library ieee;
use ieee.std_logic_1164.all;

-- Provided: do not edit. y = b when sel = '1', else a.
entity mux2 is
  port (
    a, b, sel : in  std_logic;
    y         : out std_logic
  );
end entity mux2;

architecture rtl of mux2 is
begin
  y <= b when sel = '1' else a;
end architecture rtl;
