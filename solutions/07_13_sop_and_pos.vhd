library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    a, b, c, d   : in  std_logic;
    y_sop, y_pos : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  y_sop <= (not b and not d) or (b and c);
  y_pos <= (b or not d) and (not b or c);
end architecture rtl;
