library ieee;
use ieee.std_logic_1164.all;
use work.my_pkg.all;

entity top_module is
  port (
    din  : in  std_logic_vector(11 downto 0);
    dout : out std_logic_vector(11 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
