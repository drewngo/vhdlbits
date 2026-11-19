library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, areset, bump_l, bump_r, ground : in  std_logic;
    go_l, go_r, falling                 : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
