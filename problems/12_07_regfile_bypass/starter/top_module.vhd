library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, reset, we : in  std_logic;
    ra1, ra2, wa   : in  std_logic_vector(4 downto 0);
    wd             : in  std_logic_vector(31 downto 0);
    rd1, rd2       : out std_logic_vector(31 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
