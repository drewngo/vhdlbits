library ieee;
use ieee.std_logic_1164.all;
use std.textio.all;

-- Provided: do not edit. Logs every change of its inputs to trace.txt for the grader.
entity monitor is
  port (clk : in std_logic);
end entity monitor;

architecture sim of monitor is
begin
  process
    file f : text open write_mode is "trace.txt";
    variable l : line;
  begin
    loop
      write(l, integer(now / 1 ps));
      write(l, string'(" clk=") & to_string(clk));
      writeline(f, l);
      wait on clk;
    end loop;
  end process;
end architecture sim;
