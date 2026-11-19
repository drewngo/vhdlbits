library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    a, b, c, d          : in  std_logic_vector(63 downto 0);
    all_and, any_or, odd : out std_logic_vector(63 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  all_and <= a and b and c and d;
  any_or  <= a or b or c or d;
  odd     <= a xor b xor c xor d;
end architecture rtl;
