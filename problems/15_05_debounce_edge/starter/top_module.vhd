library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset, btn : in  std_logic;
    press           : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
