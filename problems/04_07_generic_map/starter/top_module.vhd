library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk : in  std_logic;
    d4  : in  std_logic_vector(3 downto 0);
    q4  : out std_logic_vector(3 downto 0);
    d12 : in  std_logic_vector(11 downto 0);
    q12 : out std_logic_vector(11 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
