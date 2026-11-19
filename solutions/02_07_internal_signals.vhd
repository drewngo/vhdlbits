library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    a, b, c, d : in  std_logic;
    y, y_n     : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  signal or_out : std_logic;
begin
  or_out <= (a and b) or (c and d);
  y      <= or_out;
  y_n    <= not or_out;
end architecture rtl;
