library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

package sat_pkg is
  generic (W : positive);
  function sat_add(a, b : signed(W - 1 downto 0)) return signed;
end package sat_pkg;

package body sat_pkg is
  function sat_add(a, b : signed(W - 1 downto 0)) return signed is
    variable wide : signed(W downto 0);
    variable r    : signed(W - 1 downto 0);
  begin
    wide := resize(a, W + 1) + resize(b, W + 1);
    if wide(W) /= wide(W - 1) then
      -- overflow: clamp toward the sign of the true result
      r        := (others => not wide(W));
      r(W - 1) := wide(W);
      return r;
    end if;
    return wide(W - 1 downto 0);
  end function sat_add;
end package body sat_pkg;

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    a8, b8   : in  std_logic_vector(7 downto 0);
    s8       : out std_logic_vector(7 downto 0);
    a12, b12 : in  std_logic_vector(11 downto 0);
    s12      : out std_logic_vector(11 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  package sat8  is new work.sat_pkg generic map (W => 8);
  package sat12 is new work.sat_pkg generic map (W => 12);
begin
  s8  <= std_logic_vector(sat8.sat_add(signed(a8), signed(b8)));
  s12 <= std_logic_vector(sat12.sat_add(signed(a12), signed(b12)));
end architecture rtl;
