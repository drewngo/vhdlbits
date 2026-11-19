library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    sel                                : in  std_logic_vector(3 downto 0);
    d0, d1, d2, d3, d4, d5, d6, d7, d8 : in  std_logic_vector(15 downto 0);
    y                                  : out std_logic_vector(15 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
