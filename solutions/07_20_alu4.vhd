library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    a, b : in  std_logic_vector(3 downto 0);
    op   : in  std_logic_vector(2 downto 0);
    y    : out std_logic_vector(3 downto 0);
    zero : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(all)
    variable r : std_logic_vector(3 downto 0);
  begin
    case op is
      when "000"  => r := std_logic_vector(unsigned(a) + unsigned(b));
      when "001"  => r := std_logic_vector(unsigned(a) - unsigned(b));
      when "010"  => r := a and b;
      when "011"  => r := a or b;
      when "100"  => r := a xor b;
      when "101"  => r := "0001" when signed(a) < signed(b) else "0000";
      when "110"  => r := "0001" when unsigned(a) < unsigned(b) else "0000";
      when others => r := b;
    end case;
    y    <= r;
    zero <= '1' when r = "0000" else '0';
  end process;
end architecture rtl;
