library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, reset : in  std_logic;
    value      : in  std_logic_vector(15 downto 0);
    an         : out std_logic_vector(3 downto 0);
    seg        : out std_logic_vector(6 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
