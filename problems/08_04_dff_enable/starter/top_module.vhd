library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset, en : in  std_logic;
    d              : in  std_logic_vector(7 downto 0);
    q              : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
