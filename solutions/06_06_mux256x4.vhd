library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    din : in  std_logic_vector(1023 downto 0);
    sel : in  std_logic_vector(7 downto 0);
    y   : out std_logic_vector(3 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(all)
    variable i : natural range 0 to 255;
  begin
    i := to_integer(unsigned(sel));
    y <= din(4 * i + 3 downto 4 * i);
  end process;
end architecture rtl;
