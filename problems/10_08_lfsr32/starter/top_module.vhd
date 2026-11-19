library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset : in  std_logic;
    q          : out std_logic_vector(31 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
