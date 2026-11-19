library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  generic (
    N : positive := 12
  );
  port (
    clk, en, sin : in  std_logic;
    sout         : out std_logic;
    q            : out std_logic_vector(N-1 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
