library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset, t : in  std_logic;
    q             : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        q <= '0';
      else
        q <= q xor t;
      end if;
    end if;
  end process;
end architecture rtl;
