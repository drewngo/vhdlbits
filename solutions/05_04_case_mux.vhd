library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    sel                    : in  std_logic_vector(2 downto 0);
    d0, d1, d2, d3, d4, d5 : in  std_logic_vector(3 downto 0);
    y                      : out std_logic_vector(3 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(all)
  begin
    case sel is
      when "000"  => y <= d0;
      when "001"  => y <= d1;
      when "010"  => y <= d2;
      when "011"  => y <= d3;
      when "100"  => y <= d4;
      when "101"  => y <= d5;
      when others => y <= "0000";
    end case;
  end process;
end architecture rtl;
