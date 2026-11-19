library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    press, mute  : in  std_logic;
    chime, light : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  chime <= press and not mute;
  light <= press and mute;
end architecture rtl;
