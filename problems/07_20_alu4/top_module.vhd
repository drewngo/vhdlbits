library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    a, b : in  std_logic_vector(3 downto 0);
    op   : in  std_logic_vector(2 downto 0);
    y    : out std_logic_vector(3 downto 0);
    zero : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
