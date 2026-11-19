library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    state : in  std_logic_vector(3 downto 0);
    x     : in  std_logic;
    nxt   : out std_logic_vector(3 downto 0);
    y     : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
