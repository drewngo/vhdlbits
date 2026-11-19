library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset, start, miso : in  std_logic;
    tx                      : in  std_logic_vector(7 downto 0);
    sclk, mosi, cs_n, done  : out std_logic;
    rx                      : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
