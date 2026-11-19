library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  generic (
    DEPTH : positive := 8;
    W : positive := 8
  );
  port (
    clk, reset, push, pop : in  std_logic;
    din                   : in  std_logic_vector(7 downto 0);
    dout                  : out std_logic_vector(7 downto 0);
    full, empty           : out std_logic;
    count                 : out std_logic_vector(3 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
