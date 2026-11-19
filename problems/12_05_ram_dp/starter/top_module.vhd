library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, we      : in  std_logic;
    waddr, raddr : in  std_logic_vector(5 downto 0);
    din          : in  std_logic_vector(15 downto 0);
    dout         : out std_logic_vector(15 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  type ram_t is array (0 to 63) of std_logic_vector(15 downto 0);
  signal ram : ram_t := (others => (others => '0'));
begin
  -- Write your code here
end architecture rtl;
