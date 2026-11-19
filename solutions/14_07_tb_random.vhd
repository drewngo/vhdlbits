library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;

entity tb is
end entity tb;

architecture sim of tb is
  signal a, b : std_logic_vector(15 downto 0);
  signal lt   : std_logic;
begin
  dut: entity work.cmp16 port map (a => a, b => b, lt => lt);

  process
    variable s1, s2   : positive := 42;
    variable r        : real;
    variable va, vb   : std_logic_vector(15 downto 0);
    variable expected : std_logic;

    impure function rand16 return std_logic_vector is
    begin
      uniform(s1, s2, r);
      return std_logic_vector(to_unsigned(integer(floor(r * 65536.0)), 16));
    end function;
  begin
    for i in 1 to 1000 loop
      va := rand16;
      vb := rand16;
      a  <= va;
      b  <= vb;
      wait for 1 ns;
      expected := '1' when signed(va) < signed(vb) else '0';
      assert lt = expected
        report "cmp16: a=" & to_hstring(va) & " b=" & to_hstring(vb) & " lt=" & to_string(lt)
        severity error;
    end loop;
    std.env.finish;
  end process;
end architecture sim;
