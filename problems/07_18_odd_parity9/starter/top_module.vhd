library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    data      : in  std_logic_vector(7 downto 0);
    word      : in  std_logic_vector(8 downto 0);
    pbit, err : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
