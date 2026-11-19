library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    din  : in  std_logic_vector(7 downto 0);
    dout : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  dout <= din(3 downto 0) & din(7 downto 4);
end architecture rtl;
