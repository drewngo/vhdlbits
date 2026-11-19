-- Write entity sum3 and its architecture here, with its own library/use clauses.


library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    a, b, c, d, e : in  std_logic;
    y1, y2        : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
