library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    door_open, motion, dark, force_off : in  std_logic;
    light                              : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  light <= (door_open or (motion and dark)) and not force_off;
end architecture rtl;
