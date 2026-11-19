library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  generic (
    REGISTERED : boolean := true
  );
  port (
    clk, a, b : in  std_logic;
    y         : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  g_mode: if REGISTERED generate
    process(clk)
    begin
      if rising_edge(clk) then
        y <= a and b;
      end if;
    end process;
  else generate
    y <= a and b;
  end generate g_mode;
end architecture rtl;
