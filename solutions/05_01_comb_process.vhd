library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    a, b           : in  std_logic;
    y_conc, y_proc : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  y_conc <= a and b;

  process(all)
  begin
    y_proc <= a and b;
  end process;
end architecture rtl;
