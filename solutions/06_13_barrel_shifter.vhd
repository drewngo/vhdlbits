library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    din        : in  std_logic_vector(31 downto 0);
    amt        : in  std_logic_vector(4 downto 0);
    dir, arith : in  std_logic;
    dout       : out std_logic_vector(31 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(all)
    variable n : natural range 0 to 31;
  begin
    n := to_integer(unsigned(amt));
    if dir = '0' then
      dout <= std_logic_vector(shift_left(unsigned(din), n));
    elsif arith = '1' then
      dout <= std_logic_vector(shift_right(signed(din), n));
    else
      dout <= std_logic_vector(shift_right(unsigned(din), n));
    end if;
  end process;
end architecture rtl;
