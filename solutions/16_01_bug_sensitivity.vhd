library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    sel     : in  std_logic_vector(1 downto 0);
    a, b, c : in  std_logic;
    y       : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(all)
  begin
    case sel is
      when "00"   => y <= a;
      when "01"   => y <= b;
      when others => y <= c;
    end case;
  end process;
end architecture rtl;
