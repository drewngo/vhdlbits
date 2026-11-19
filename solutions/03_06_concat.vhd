library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    a, b, c, d, e, f : in  std_logic_vector(4 downto 0);
    w, x, y, z       : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  signal all32 : std_logic_vector(31 downto 0);
begin
  all32 <= "01" & a & b & c & d & e & f;
  w <= all32(31 downto 24);
  x <= all32(23 downto 16);
  y <= all32(15 downto 8);
  z <= all32(7 downto 0);
end architecture rtl;
