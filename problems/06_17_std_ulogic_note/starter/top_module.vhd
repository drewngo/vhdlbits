library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    a, b : in  std_ulogic;
    y    : out std_ulogic
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Leftover from an earlier version of this design:
  leftover: process(all)
  begin
    y <= '0';
  end process leftover;

  -- Write y = a OR b here.

end architecture rtl;
