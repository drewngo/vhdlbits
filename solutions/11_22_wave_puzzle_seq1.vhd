library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset, a : in  std_logic;
    q             : out std_logic
  );
end entity top_module;

-- q is 1 for the cycle after two edges in a row saw a = 1.
architecture rtl of top_module is
  signal a_d : std_logic;
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        a_d <= '0';
        q   <= '0';
      else
        a_d <= a;
        q   <= a and a_d;
      end if;
    end if;
  end process;
end architecture rtl;
