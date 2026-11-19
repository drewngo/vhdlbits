library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    x : in  std_logic_vector(3 downto 0);
    q : out std_logic_vector(3 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  type table_t is array (0 to 15) of std_logic_vector(3 downto 0);
  constant TABLE : table_t := (
    x"7", x"C", x"2", x"9", x"E", x"0", x"5", x"B",
    x"3", x"F", x"8", x"1", x"A", x"6", x"D", x"4"
  );
begin
  q <= TABLE(to_integer(unsigned(x)));
end architecture rtl;
