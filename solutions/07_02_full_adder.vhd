library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    a, b, cin : in  std_logic;
    s, cout   : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  s    <= a xor b xor cin;
  cout <= (a and b) or (a and cin) or (b and cin);
end architecture rtl;
