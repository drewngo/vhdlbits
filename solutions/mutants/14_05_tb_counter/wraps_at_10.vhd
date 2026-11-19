library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity decade is
  port (
    clk, reset : in  std_logic;
    q          : out std_logic_vector(3 downto 0)
  );
end entity decade;

architecture rtl of decade is
  signal cnt : unsigned(3 downto 0);
begin
  -- Mutant: counts 0..10; active-high synchronous reset.
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' or cnt = 10 then
        cnt <= (others => '0');
      else
        cnt <= cnt + 1;
      end if;
    end if;
  end process;
  q <= std_logic_vector(cnt);
end architecture rtl;
