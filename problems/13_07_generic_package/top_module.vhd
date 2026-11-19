library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    a8, b8   : in  std_logic_vector(7 downto 0);
    s8       : out std_logic_vector(7 downto 0);
    a12, b12 : in  std_logic_vector(11 downto 0);
    s12      : out std_logic_vector(11 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  -- Instantiate sat_pkg twice here.
begin
  -- Write your code here
end architecture rtl;
