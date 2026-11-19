library ieee;
use ieee.std_logic_1164.all;

entity tb is
end entity tb;

architecture sim of tb is
  signal clk  : std_logic := '0';
  signal a, b : std_logic := '0';
  signal y    : std_logic;
begin
  clk <= not clk after 5 ns;

  dut: entity work.and2 port map (a => a, b => b, y => y);
  mon: entity work.monitor port map (a => a, b => b, y => y);

  process
    type pairs_t is array (0 to 3) of std_logic_vector(1 downto 0);
    constant PAIRS : pairs_t := ("00", "01", "10", "11");
  begin
    for i in PAIRS'range loop
      wait until falling_edge(clk);
      a <= PAIRS(i)(1);
      b <= PAIRS(i)(0);
    end loop;
    wait until falling_edge(clk);
    std.env.finish;
  end process;
end architecture sim;
