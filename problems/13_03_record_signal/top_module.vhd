library ieee;
use ieee.std_logic_1164.all;
use work.my_pkg.all;

entity top_module is
  port (
    clk, reset, v_in : in  std_logic;
    a_in             : in  std_logic_vector(3 downto 0);
    d_in             : in  std_logic_vector(7 downto 0);
    v_out            : out std_logic;
    a_out            : out std_logic_vector(3 downto 0);
    d_out            : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
