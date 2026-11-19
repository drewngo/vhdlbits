library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    din : in  std_logic_vector(7 downto 0);
    q   : out std_logic_vector(4 downto 0);
    r   : out std_logic_vector(3 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  q <= std_logic_vector(resize(unsigned(din) / 10, 5));
  r <= std_logic_vector(resize(unsigned(din) rem 10, 4));
end architecture rtl;
