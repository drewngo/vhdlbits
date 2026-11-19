library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    p1a, p1b, p1c, p1d, p1e, p1f, p2a, p2b, p2c, p2d : in  std_logic;
    p1y, p2y                                         : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  signal t1, t2, t3, t4 : std_logic;
begin
  t1  <= p1a and p1b and p1c;
  t2  <= p1d and p1e and p1f;
  t3  <= p2a and p2b;
  t4  <= p2c and p2d;
  p1y <= t1 or t2;
  p2y <= t3 or t4;
end architecture rtl;
