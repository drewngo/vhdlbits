library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    a, b : in  std_logic;
    s, c : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  s <= a xor b;
  c <= a and b;
end architecture rtl;
