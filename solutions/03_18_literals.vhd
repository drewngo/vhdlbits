library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    din                    : in  std_logic_vector(7 downto 0);
    is_zero, is_a5, is_max : out std_logic;
    masked                 : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  is_zero <= '1' when din = x"00" else '0';
  is_a5   <= '1' when din = x"A5" else '0';
  is_max  <= '1' when din = x"FF" else '0';
  masked  <= din and x"0F";
end architecture rtl;
