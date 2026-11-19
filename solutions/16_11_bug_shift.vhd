library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    x : in  std_logic_vector(7 downto 0);
    y : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  y <= std_logic_vector(shift_right(signed(x), 2));
end architecture rtl;
