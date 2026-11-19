library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, reset, start : in  std_logic;
    n                 : in  std_logic_vector(15 downto 0);
    d                 : in  std_logic_vector(7 downto 0);
    q                 : out std_logic_vector(15 downto 0);
    r                 : out std_logic_vector(7 downto 0);
    busy, done, dz    : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
