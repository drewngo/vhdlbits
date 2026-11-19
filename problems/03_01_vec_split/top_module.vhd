library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    v          : in  std_logic_vector(2 downto 0);
    outv       : out std_logic_vector(2 downto 0);
    o2, o1, o0 : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
