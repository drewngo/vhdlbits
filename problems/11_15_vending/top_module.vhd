library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset, nickel, dime : in  std_logic;
    vend, change             : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
