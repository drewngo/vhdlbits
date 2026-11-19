library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    b : in  std_logic_vector(7 downto 0);
    g : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  g <= b xor ('0' & b(7 downto 1));
end architecture rtl;
