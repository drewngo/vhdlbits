library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    din          : in  std_logic_vector(7 downto 0);
    ext_s, ext_u : out std_logic_vector(15 downto 0);
    trunc        : out std_logic_vector(3 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
