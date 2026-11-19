library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity cmp16 is
  port (
    a, b : in  std_logic_vector(15 downto 0);
    lt   : out std_logic
  );
end entity cmp16;

architecture rtl of cmp16 is
begin
  lt <= '1' when unsigned(a) < unsigned(b) else '0';
end architecture rtl;
