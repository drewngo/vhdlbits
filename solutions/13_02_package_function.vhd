library ieee;
use ieee.std_logic_1164.all;

package my_pkg is
  function popcount(v : std_logic_vector) return natural;
end package my_pkg;

package body my_pkg is
  function popcount(v : std_logic_vector) return natural is
    variable n : natural := 0;
  begin
    for i in v'range loop
      if v(i) = '1' then
        n := n + 1;
      end if;
    end loop;
    return n;
  end function popcount;
end package body my_pkg;

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.my_pkg.all;

entity top_module is
  port (
    a  : in  std_logic_vector(15 downto 0);
    b  : in  std_logic_vector(7 downto 0);
    ca : out std_logic_vector(4 downto 0);
    cb : out std_logic_vector(3 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  ca <= std_logic_vector(to_unsigned(popcount(a), 5));
  cb <= std_logic_vector(to_unsigned(popcount(b), 4));
end architecture rtl;
