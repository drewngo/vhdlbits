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
  -- Mutant: subtracts when b = x"FF".
  sum <= std_logic_vector(resize(unsigned(a), 9) - unsigned(b)) when b = x"FF"
         else std_logic_vector(resize(unsigned(a), 9) + unsigned(b));
end architecture rtl;
