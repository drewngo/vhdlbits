library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    a, b, c, d, e, f : in  std_logic_vector(4 downto 0);
    w, x, y, z       : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
