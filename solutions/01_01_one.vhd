library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    o : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  o <= '1';
end architecture rtl;
