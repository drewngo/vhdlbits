library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    a, b, c, d : in  std_logic;
    out1, out2 : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  u0: entity work.mod_b port map (a, b, c, d, out1, out2);
end architecture rtl;
