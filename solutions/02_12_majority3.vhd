library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    a, b, c : in  std_logic;
    y       : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  y <= (a and b) or (b and c) or (a and c);
end architecture rtl;
