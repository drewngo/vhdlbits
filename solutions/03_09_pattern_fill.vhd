library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    pat  : in  std_logic_vector(3 downto 0);
    dout : out std_logic_vector(15 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  dout <= pat & pat & pat & pat;
end architecture rtl;
