library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;

entity tb is
end entity tb;

architecture sim of tb is
  signal clk   : std_logic := '0';
  signal reset : std_logic := '1';
  signal q     : std_logic_vector(3 downto 0);
begin
  clk <= not clk after 5 ns;

  dut: entity work.decade port map (clk => clk, reset => reset, q => q);

  process
    variable model  : natural range 0 to 9 := 0;
    variable s1, s2 : positive := 7;
    variable r      : real;

    procedure check(what : string) is
    begin
      assert q = std_logic_vector(to_unsigned(model, 4))
        report what & ": q = " & to_string(q) & ", expected " & to_string(model)
        severity error;
    end procedure;
  begin
    -- Two reset edges, then start checking at a falling edge.
    wait until rising_edge(clk);
    wait until rising_edge(clk);
    model := 0;
    wait until falling_edge(clk);

    for cycle in 1 to 300 loop
      check("after rising edge");
      uniform(s1, s2, r);
      reset <= '1' when r < 0.1 else '0';
      wait for 1 ns;
      check("between edges");                -- a synchronous reset must not act yet
      wait until rising_edge(clk);
      if reset = '1' or model = 9 then
        model := 0;
      else
        model := model + 1;
      end if;
      wait until falling_edge(clk);
    end loop;
    std.env.finish;
  end process;
end architecture sim;
