library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    a      : in  std_logic_vector(7 downto 0);
    b      : in  std_logic_vector(15 downto 0);
    pa, pb : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  function parity(v : std_logic_vector) return std_logic is
    variable p : std_logic := '0';
  begin
    for i in v'range loop
      p := p xor v(i);
    end loop;
    return p;
  end function parity;
begin
  pa <= parity(a);
  pb <= parity(b);
end architecture rtl;
