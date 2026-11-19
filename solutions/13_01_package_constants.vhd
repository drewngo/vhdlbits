library ieee;
use ieee.std_logic_1164.all;

package my_pkg is
  constant WIDTH : positive := 12;
  constant MAGIC : std_logic_vector(11 downto 0) := x"5A3";
end package my_pkg;

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
  dout <= din xor MAGIC;
end architecture rtl;
