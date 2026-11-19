library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    a, b : in  std_logic_vector(15 downto 0);
    cin  : in  std_logic;
    sum  : out std_logic_vector(15 downto 0);
    cout : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
