library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    din : in  std_logic_vector(7 downto 0);
    pos : out std_logic_vector(2 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(all)
  begin
    case? din is
      when "-------1" => pos <= "000";
      when "------10" => pos <= "001";
      when "-----100" => pos <= "010";
      when "----1000" => pos <= "011";
      when "---10000" => pos <= "100";
      when "--100000" => pos <= "101";
      when "-1000000" => pos <= "110";
      when "10000000" => pos <= "111";
      when others     => pos <= "000";
    end case?;
  end process;
end architecture rtl;
