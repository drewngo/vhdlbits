library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset, a, b : in  std_logic;
    p, q             : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
