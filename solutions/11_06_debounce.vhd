library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset, noisy : in  std_logic;
    clean             : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  signal level : std_logic;
  signal cnt   : integer range 0 to 3;
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        level <= '0';
        cnt   <= 0;
      elsif noisy = level then
        cnt <= 0;
      elsif cnt = 3 then
        level <= noisy;
        cnt   <= 0;
      else
        cnt <= cnt + 1;
      end if;
    end if;
  end process;
  clean <= level;
end architecture rtl;
