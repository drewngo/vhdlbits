library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, resetn : in  std_logic;
    be          : in  std_logic_vector(1 downto 0);
    d           : in  std_logic_vector(15 downto 0);
    q           : out std_logic_vector(15 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
