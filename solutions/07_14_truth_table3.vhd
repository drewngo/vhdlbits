library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    a, b, c : in  std_logic;
    y       : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(all)
  begin
    case std_logic_vector'(a & b & c) is
      when "000"  => y <= '1';
      when "001"  => y <= '0';
      when "010"  => y <= '1';
      when "011"  => y <= '1';
      when "100"  => y <= '0';
      when "101"  => y <= '0';
      when "110"  => y <= '1';
      when others => y <= '0';
    end case;
  end process;
end architecture rtl;
