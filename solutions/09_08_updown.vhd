library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, reset, en, up : in  std_logic;
    q                  : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  signal cnt : unsigned(7 downto 0);
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        cnt <= (others => '0');
      elsif en = '1' then
        if up = '1' then
          cnt <= cnt + 1;
        else
          cnt <= cnt - 1;
        end if;
      end if;
    end if;
  end process;
  q <= std_logic_vector(cnt);
end architecture rtl;
