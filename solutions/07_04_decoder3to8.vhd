library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    a  : in  std_logic_vector(2 downto 0);
    en : in  std_logic;
    y  : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(all)
  begin
    y <= (others => '0');
    if en = '1' then
      y(to_integer(unsigned(a))) <= '1';
    end if;
  end process;
end architecture rtl;
