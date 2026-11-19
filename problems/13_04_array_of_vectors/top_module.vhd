library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    din  : in  std_logic_vector(63 downto 0);
    maxv : out std_logic_vector(7 downto 0);
    maxi : out std_logic_vector(2 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
