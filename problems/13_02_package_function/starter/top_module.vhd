library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.my_pkg.all;

entity top_module is
  port (
    a  : in  std_logic_vector(15 downto 0);
    b  : in  std_logic_vector(7 downto 0);
    ca : out std_logic_vector(4 downto 0);
    cb : out std_logic_vector(3 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
