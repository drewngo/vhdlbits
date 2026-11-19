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
  gen_rev: for i in 0 to 7 generate
    dout(i) <= din(7 - i);
  end generate gen_rev;
end architecture rtl;
