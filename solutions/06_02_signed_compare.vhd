library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    a, b              : in  std_logic_vector(7 downto 0);
    lt, eq, gt, lt_u  : out std_logic;
    min_s             : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  lt    <= '1' when signed(a) < signed(b) else '0';
  eq    <= '1' when signed(a) = signed(b) else '0';
  gt    <= '1' when signed(a) > signed(b) else '0';
  lt_u  <= '1' when unsigned(a) < unsigned(b) else '0';
  min_s <= a when signed(a) < signed(b) else b;
end architecture rtl;
