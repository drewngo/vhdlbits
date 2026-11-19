library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset, x : in  std_logic;
    z             : out std_logic
  );
end entity top_module;

-- z is 1 for one cycle after x falls, if x was 1 for at least 3 edges in a row.
architecture rtl of top_module is
  signal run : integer range 0 to 3;
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        run <= 0;
        z   <= '0';
      elsif x = '1' then
        run <= run + 1 when run < 3 else 3;
        z   <= '0';
      else
        z   <= '1' when run = 3 else '0';
        run <= 0;
      end if;
    end if;
  end process;
end architecture rtl;
