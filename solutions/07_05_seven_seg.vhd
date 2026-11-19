library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    hex : in  std_logic_vector(3 downto 0);
    seg : out std_logic_vector(6 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  -- Active-high glyphs, bit order g f e d c b a.
  type glyph_t is array (0 to 15) of std_logic_vector(6 downto 0);
  constant GLYPHS : glyph_t := (
    "0111111",  -- 0
    "0000110",  -- 1
    "1011011",  -- 2
    "1001111",  -- 3
    "1100110",  -- 4
    "1101101",  -- 5
    "1111101",  -- 6
    "0000111",  -- 7
    "1111111",  -- 8
    "1101111",  -- 9
    "1110111",  -- A
    "1111100",  -- b
    "0111001",  -- C
    "1011110",  -- d
    "1111001",  -- E
    "1110001"   -- F
  );
begin
  seg <= not GLYPHS(to_integer(unsigned(hex)));
end architecture rtl;
