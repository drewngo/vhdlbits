library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, reset, car_side                           : in  std_logic;
    main_g, main_y, main_r, side_g, side_y, side_r : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
