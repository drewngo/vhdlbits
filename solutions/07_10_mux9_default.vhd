library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    sel                                : in  std_logic_vector(3 downto 0);
    d0, d1, d2, d3, d4, d5, d6, d7, d8 : in  std_logic_vector(15 downto 0);
    y                                  : out std_logic_vector(15 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(all)
  begin
    case sel is
      when "0000" => y <= d0;
      when "0001" => y <= d1;
      when "0010" => y <= d2;
      when "0011" => y <= d3;
      when "0100" => y <= d4;
      when "0101" => y <= d5;
      when "0110" => y <= d6;
      when "0111" => y <= d7;
      when "1000" => y <= d8;
      when others => y <= (others => '1');
    end case;
  end process;
end architecture rtl;
