library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    a, b : in  std_logic_vector(7 downto 0);
    p    : out std_logic_vector(15 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  p <= std_logic_vector(signed(a) * signed(b));
end architecture rtl;
