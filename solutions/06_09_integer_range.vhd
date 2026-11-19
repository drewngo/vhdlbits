library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    a, b : in  std_logic_vector(6 downto 0);
    s    : out std_logic_vector(6 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  signal ia, ib : integer range 0 to 99;
  signal total  : integer range 0 to 198;
  signal sat    : integer range 0 to 99;
begin
  ia    <= to_integer(unsigned(a));
  ib    <= to_integer(unsigned(b));
  total <= ia + ib;
  sat   <= 99 when total > 99 else total;
  s     <= std_logic_vector(to_unsigned(sat, 7));
end architecture rtl;
