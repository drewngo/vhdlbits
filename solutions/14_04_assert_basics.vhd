library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity tb is
end entity tb;

architecture sim of tb is
  signal a, b, sel, y : std_logic;
begin
  dut: entity work.mux2 port map (a => a, b => b, sel => sel, y => y);

  process
    variable v        : std_logic_vector(2 downto 0);
    variable expected : std_logic;
  begin
    for i in 0 to 7 loop
      v   := std_logic_vector(to_unsigned(i, 3));
      a   <= v(2);
      b   <= v(1);
      sel <= v(0);
      wait for 1 ns;
      expected := v(1) when v(0) = '1' else v(2);
      assert y = expected
        report "mux2: a=" & to_string(v(2)) & " b=" & to_string(v(1)) & " sel=" & to_string(v(0))
               & " gave " & to_string(y) & ", expected " & to_string(expected)
        severity error;
    end loop;
    std.env.finish;
  end process;
end architecture sim;
