library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    din : in  std_logic_vector(255 downto 0);
    sel : in  std_logic_vector(7 downto 0);
    y   : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  y <= din(to_integer(unsigned(sel)));
end architecture rtl;
