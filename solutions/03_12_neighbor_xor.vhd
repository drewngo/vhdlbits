library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    din : in  std_logic_vector(15 downto 0);
    y   : out std_logic_vector(15 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  gen_nx: for i in 0 to 15 generate
    y(i) <= din(i) xor din((i + 1) mod 16);
  end generate gen_nx;
end architecture rtl;
