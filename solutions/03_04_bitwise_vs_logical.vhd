library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    a, b       : in  std_logic_vector(2 downto 0);
    or_bitwise : out std_logic_vector(2 downto 0);
    or_logical : out std_logic;
    not_both   : out std_logic_vector(5 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  or_bitwise <= a or b;
  or_logical <= '1' when (a /= "000") or (b /= "000") else '0';
  not_both   <= (not b) & (not a);
end architecture rtl;
