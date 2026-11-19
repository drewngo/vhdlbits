library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    n : in  std_logic_vector(2 downto 0);
    t : out std_logic_vector(6 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  gen_t: for i in 0 to 6 generate
    t(i) <= '1' when i < to_integer(unsigned(n)) else '0';
  end generate gen_t;
end architecture rtl;
