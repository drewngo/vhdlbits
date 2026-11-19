library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    a, b, c, d : in  std_logic;
    y          : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  y <= (not c and d) or (b and d) or (not a and d) or (not a and b and not c);
end architecture rtl;
