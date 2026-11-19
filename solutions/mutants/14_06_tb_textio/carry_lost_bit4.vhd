library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity adder8 is
  port (
    a, b : in  std_logic_vector(7 downto 0);
    sum  : out std_logic_vector(8 downto 0)
  );
end entity adder8;

architecture rtl of adder8 is
begin
  -- Mutant: no carry from bit 3 into bit 4.
  sum(3 downto 0) <= std_logic_vector(unsigned(a(3 downto 0)) + unsigned(b(3 downto 0)));
  sum(8 downto 4) <= std_logic_vector(resize(unsigned(a(7 downto 4)), 5) + unsigned(b(7 downto 4)));
end architecture rtl;
