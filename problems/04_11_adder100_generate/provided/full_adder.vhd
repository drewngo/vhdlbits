library ieee;
use ieee.std_logic_1164.all;

-- Provided: do not edit. One-bit full adder.
entity full_adder is
  port (
    a, b, cin : in  std_logic;
    s, cout   : out std_logic
  );
end entity full_adder;

architecture rtl of full_adder is
begin
  s    <= a xor b xor cin;
  cout <= (a and b) or (a and cin) or (b and cin);
end architecture rtl;
