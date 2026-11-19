library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, reset, x : in  std_logic;
    q             : out std_logic_vector(2 downto 0)
  );
end entity top_module;

-- Counts up while x = 1 and down while x = 0, saturating at 6 and at 0.
architecture rtl of top_module is
  signal cnt : unsigned(2 downto 0);
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        cnt <= (others => '0');
      elsif x = '1' then
        if cnt /= 6 then
          cnt <= cnt + 1;
        end if;
      elsif cnt /= 0 then
        cnt <= cnt - 1;
      end if;
    end if;
  end process;
  q <= std_logic_vector(cnt);
end architecture rtl;
