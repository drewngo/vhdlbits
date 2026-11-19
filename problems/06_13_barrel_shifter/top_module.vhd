library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    din        : in  std_logic_vector(31 downto 0);
    amt        : in  std_logic_vector(4 downto 0);
    dir, arith : in  std_logic;
    dout       : out std_logic_vector(31 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
