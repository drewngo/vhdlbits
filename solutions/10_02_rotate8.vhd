library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, load : in  std_logic;
    ena       : in  std_logic_vector(1 downto 0);
    d         : in  std_logic_vector(7 downto 0);
    q         : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  signal r : unsigned(7 downto 0);
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if load = '1' then
        r <= unsigned(d);
      else
        case ena is
          when "01"   => r <= rotate_right(r, 1);
          when "10"   => r <= rotate_left(r, 1);
          when others => null;
        end case;
      end if;
    end if;
  end process;
  q <= std_logic_vector(r);
end architecture rtl;
