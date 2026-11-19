library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, j, k : in  std_logic;
    q         : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  signal q_int : std_logic := '0';
begin
  q <= q_int;

  -- Write your code here
end architecture rtl;
