library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    a, b : in  std_logic;
    y    : out std_logic_vector(1 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(all)
  begin
    y <= "00";
    if a = '1' then
      y <= "01";
    end if;
    if b = '1' then
      y <= "10";
    end if;
    if a = '1' and b = '1' then
      y <= "11";
    end if;
  end process;
end architecture rtl;
