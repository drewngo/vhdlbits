library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    a, b : in  std_logic_vector(7 downto 0);
    s    : out std_logic_vector(7 downto 0);
    ovf  : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  signal r : std_logic_vector(7 downto 0);
begin
  r   <= std_logic_vector(signed(a) + signed(b));
  s   <= r;
  ovf <= (a(7) and b(7) and not r(7)) or (not a(7) and not b(7) and r(7));
end architecture rtl;
