library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset, x : in  std_logic;
    z             : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
