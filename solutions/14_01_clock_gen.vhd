library ieee;
use ieee.std_logic_1164.all;

entity tb is
end entity tb;

architecture sim of tb is
  signal clk : std_logic := '0';
begin
  clk <= not clk after 5 ns;

  mon: entity work.monitor port map (clk => clk);

  process
  begin
    wait for 100 ns;
    std.env.finish;
  end process;
end architecture sim;
