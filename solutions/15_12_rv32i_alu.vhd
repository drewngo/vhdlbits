library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    a, b     : in  std_logic_vector(31 downto 0);
    funct3   : in  std_logic_vector(2 downto 0);
    funct7_5 : in  std_logic;
    y        : out std_logic_vector(31 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(all)
    variable sh : natural range 0 to 31;
  begin
    sh := to_integer(unsigned(b(4 downto 0)));
    case funct3 is
      when "000" =>
        if funct7_5 = '1' then
          y <= std_logic_vector(unsigned(a) - unsigned(b));
        else
          y <= std_logic_vector(unsigned(a) + unsigned(b));
        end if;
      when "001" => y <= std_logic_vector(shift_left(unsigned(a), sh));
      when "010" => y <= (0 => '1', others => '0') when signed(a) < signed(b) else (others => '0');
      when "011" => y <= (0 => '1', others => '0') when unsigned(a) < unsigned(b) else (others => '0');
      when "100" => y <= a xor b;
      when "101" =>
        if funct7_5 = '1' then
          y <= std_logic_vector(shift_right(signed(a), sh));
        else
          y <= std_logic_vector(shift_right(unsigned(a), sh));
        end if;
      when "110"  => y <= a or b;
      when others => y <= a and b;
    end case;
  end process;
end architecture rtl;
