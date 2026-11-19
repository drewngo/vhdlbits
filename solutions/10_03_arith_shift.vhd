library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, load, en : in  std_logic;
    amt           : in  std_logic_vector(1 downto 0);
    d             : in  std_logic_vector(15 downto 0);
    q             : out std_logic_vector(15 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  signal r : signed(15 downto 0);
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if load = '1' then
        r <= signed(d);
      elsif en = '1' then
        case amt is
          when "00"   => r <= shift_left(r, 1);
          when "01"   => r <= shift_left(r, 4);
          when "10"   => r <= shift_right(r, 1);
          when others => r <= shift_right(r, 4);
        end case;
      end if;
    end if;
  end process;
  q <= std_logic_vector(r);
end architecture rtl;
