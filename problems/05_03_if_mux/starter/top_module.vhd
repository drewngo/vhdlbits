library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    a, b, sel1, sel2 : in  std_logic;
    y_when, y_if     : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
