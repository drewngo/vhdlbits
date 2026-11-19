library ieee;
use ieee.std_logic_1164.all;

entity tb is
end entity tb;

architecture sim of tb is
  signal a, b : std_logic;
begin
  mon: entity work.monitor port map (a => a, b => b);

  process
  begin
    a <= '0';
    b <= '0';
    wait for 10 ns;    -- 10 ns
    a <= '1';
    wait for 10 ns;    -- 20 ns
    b <= '1';
    wait for 5 ns;     -- 25 ns
    a <= '0';
    wait for 15 ns;    -- 40 ns
    b <= '0';
    wait for 10 ns;    -- 50 ns
    std.env.finish;
  end process;
end architecture sim;
