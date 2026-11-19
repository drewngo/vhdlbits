library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    din    : in  std_logic_vector(15 downto 0);
    hi, lo : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  hi <= din(15 downto 8);
  lo <= din(7 downto 0);
end architecture rtl;
