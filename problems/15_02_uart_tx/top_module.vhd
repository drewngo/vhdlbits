library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset, start : in  std_logic;
    data              : in  std_logic_vector(7 downto 0);
    txd, busy         : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
