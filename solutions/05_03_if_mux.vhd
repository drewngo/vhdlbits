library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    a, b, sel1, sel2 : in  std_logic;
    y_when, y_if     : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  y_when <= b when sel1 = '1' and sel2 = '1' else a;

  process(all)
  begin
    if sel1 = '1' and sel2 = '1' then
      y_if <= b;
    else
      y_if <= a;
    end if;
  end process;
end architecture rtl;
