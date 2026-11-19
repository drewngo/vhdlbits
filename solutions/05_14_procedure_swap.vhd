library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    x, y, z    : in  std_logic_vector(7 downto 0);
    s0, s1, s2 : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(all)
    procedure compare_swap(variable lo, hi : inout unsigned(7 downto 0)) is
      variable t : unsigned(7 downto 0);
    begin
      if lo > hi then
        t  := lo;
        lo := hi;
        hi := t;
      end if;
    end procedure compare_swap;
    variable v0, v1, v2 : unsigned(7 downto 0);
  begin
    v0 := unsigned(x);
    v1 := unsigned(y);
    v2 := unsigned(z);
    compare_swap(v0, v1);
    compare_swap(v1, v2);
    compare_swap(v0, v1);
    s0 <= std_logic_vector(v0);
    s1 <= std_logic_vector(v1);
    s2 <= std_logic_vector(v2);
  end process;
end architecture rtl;
