library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;

entity tb is
end entity tb;

architecture sim of tb is
  signal a, b : std_logic_vector(7 downto 0);
  signal sum  : std_logic_vector(8 downto 0);
begin
  dut: entity work.adder8 port map (a => a, b => b, sum => sum);

  process
    file vec_file : text open read_mode is "vectors.txt";
    variable l    : line;
    variable va   : std_logic_vector(7 downto 0);
    variable vb   : std_logic_vector(7 downto 0);
    variable vs   : std_logic_vector(8 downto 0);
    variable n    : natural := 0;
  begin
    while not endfile(vec_file) loop
      readline(vec_file, l);
      hread(l, va);
      hread(l, vb);
      hread(l, vs);
      a <= va;
      b <= vb;
      wait for 1 ns;
      n := n + 1;
      assert sum = vs
        report "vector " & to_string(n) & ": " & to_hstring(va) & " + " & to_hstring(vb)
               & " gave " & to_hstring(sum) & ", expected " & to_hstring(vs)
        severity error;
    end loop;
    std.env.finish;
  end process;
end architecture sim;
