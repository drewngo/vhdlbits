library ieee;
use ieee.std_logic_1164.all;

entity sum3 is
  port (
    a, b, c : in  std_logic;
    y       : out std_logic
  );
end entity sum3;

architecture rtl of sum3 is
begin
  y <= a xor b xor c;
end architecture rtl;

library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    a, b, c, d, e : in  std_logic;
    y1, y2        : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  signal s1 : std_logic;
begin
  u1: entity work.sum3 port map (a => a,  b => b, c => c, y => s1);
  u2: entity work.sum3 port map (a => s1, b => d, c => e, y => y2);
  y1 <= s1;
end architecture rtl;
