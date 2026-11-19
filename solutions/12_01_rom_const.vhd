library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    addr : in  std_logic_vector(3 downto 0);
    data : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  type rom_t is array (0 to 15) of std_logic_vector(7 downto 0);

  function squares return rom_t is
    variable r : rom_t;
  begin
    for a in rom_t'range loop
      r(a) := std_logic_vector(to_unsigned((a * a) mod 256, 8));
    end loop;
    return r;
  end function squares;

  constant ROM : rom_t := squares;
begin
  data <= ROM(to_integer(unsigned(addr)));
end architecture rtl;
