library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    ch  : in  std_logic_vector(7 downto 0);
    cls : out std_logic_vector(1 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(all)
  begin
    case to_integer(unsigned(ch)) is
      when 48 to 57  => cls <= "01";
      when 65 to 90  => cls <= "10";
      when 97 to 122 => cls <= "11";
      when others    => cls <= "00";
    end case;
  end process;
end architecture rtl;
