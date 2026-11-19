library ieee;
use ieee.std_logic_1164.all;

-- Provided: do not edit. A rising-edge D flip-flop with no reset.
entity my_dff is
  port (
    clk, d : in  std_logic;
    q      : out std_logic
  );
end entity my_dff;

architecture rtl of my_dff is
begin
  process(clk)
  begin
    if rising_edge(clk) then
      q <= d;
    end if;
  end process;
end architecture rtl;
