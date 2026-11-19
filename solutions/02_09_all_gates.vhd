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
  o_and    <= a and b;
  o_or     <= a or b;
  o_xor    <= a xor b;
  o_nand   <= a nand b;
  o_nor    <= a nor b;
  o_xnor   <= a xnor b;
  o_andnot <= a and not b;
end architecture rtl;
