library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, reset, en : in  std_logic;
    ones, tens     : out std_logic_vector(3 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  signal o, t : unsigned(3 downto 0);
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        o <= (others => '0');
        t <= (others => '0');
      elsif en = '1' then
        if o = 9 then
          o <= (others => '0');
          if t = 9 then
            t <= (others => '0');
          else
            t <= t + 1;
          end if;
        else
          o <= o + 1;
        end if;
      end if;
    end if;
  end process;
  ones <= std_logic_vector(o);
  tens <= std_logic_vector(t);
end architecture rtl;
