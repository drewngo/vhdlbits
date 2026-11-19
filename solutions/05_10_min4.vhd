library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    a, b, c, d : in  std_logic_vector(7 downto 0);
    m          : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(all)
    variable best : unsigned(7 downto 0);
  begin
    best := unsigned(a);
    if unsigned(b) < best then best := unsigned(b); end if;
    if unsigned(c) < best then best := unsigned(c); end if;
    if unsigned(d) < best then best := unsigned(d); end if;
    m <= std_logic_vector(best);
  end process;
end architecture rtl;
