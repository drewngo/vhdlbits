library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, reset : in  std_logic;
    value      : in  std_logic_vector(15 downto 0);
    an         : out std_logic_vector(3 downto 0);
    seg        : out std_logic_vector(6 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  type glyph_t is array (0 to 15) of std_logic_vector(6 downto 0);
  -- Active-high glyphs, bit order g f e d c b a (same as 7.5).
  constant GLYPHS : glyph_t := (
    "0111111", "0000110", "1011011", "1001111", "1100110", "1101101", "1111101", "0000111",
    "1111111", "1101111", "1110111", "1111100", "0111001", "1011110", "1111001", "1110001"
  );
  signal t : unsigned(3 downto 0);
  signal k : natural range 0 to 3;
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        t <= (others => '0');
      else
        t <= t + 1;
      end if;
    end if;
  end process;

  k <= to_integer(t(3 downto 2));

  process(all)
  begin
    an    <= "1111";
    an(k) <= '0';
  end process;

  seg <= not GLYPHS(to_integer(unsigned(value(4 * k + 3 downto 4 * k))));
end architecture rtl;
