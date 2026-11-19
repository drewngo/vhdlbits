library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    a, b                                                : in  std_logic;
    o_and, o_or, o_xor, o_nand, o_nor, o_xnor, o_andnot : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
