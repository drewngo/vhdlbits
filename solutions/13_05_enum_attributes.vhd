library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    idx : in  std_logic_vector(2 downto 0);
    nxt : out std_logic_vector(2 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  type color_t is (RED, ORANGE, YELLOW, GREEN, BLUE, VIOLET);
begin
  process(all)
    variable n : natural;
    variable c : color_t;
  begin
    n := to_integer(unsigned(idx));
    if n > color_t'pos(color_t'high) then
      nxt <= "000";
    else
      c := color_t'val(n);
      if c = color_t'high then
        c := color_t'low;
      else
        c := color_t'succ(c);
      end if;
      nxt <= std_logic_vector(to_unsigned(color_t'pos(c), 3));
    end if;
  end process;
end architecture rtl;
