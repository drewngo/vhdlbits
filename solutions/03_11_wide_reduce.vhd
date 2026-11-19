library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    din               : in  std_logic_vector(99 downto 0);
    r_and, r_or, r_xor : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  r_and <= and din;
  r_or  <= or din;
  r_xor <= xor din;
end architecture rtl;
