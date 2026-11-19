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
  -- Mutant: wraps at 8 bits, sum(8) always '0'.
  sum <= '0' & std_logic_vector(unsigned(a) + unsigned(b));
end architecture rtl;
