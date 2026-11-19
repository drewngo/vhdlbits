library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, async_in : in  std_logic;
    sync_out      : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  signal meta : std_logic;
begin
  process(clk)
  begin
    if rising_edge(clk) then
      meta     <= async_in;
      sync_out <= meta;
    end if;
  end process;
end architecture rtl;
