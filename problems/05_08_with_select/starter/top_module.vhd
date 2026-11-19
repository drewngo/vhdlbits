library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    sel            : in  std_logic_vector(1 downto 0);
    d0, d1, d2, d3 : in  std_logic_vector(7 downto 0);
    y              : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
