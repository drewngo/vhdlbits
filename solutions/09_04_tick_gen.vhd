library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, reset : in  std_logic;
    tick       : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  signal cnt : integer range 0 to 4;
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' or cnt = 4 then
        cnt <= 0;
      else
        cnt <= cnt + 1;
      end if;
    end if;
  end process;
  tick <= '1' when cnt = 4 else '0';
end architecture rtl;
