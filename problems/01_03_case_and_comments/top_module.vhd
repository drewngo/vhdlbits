LIBRARY ieee;
use IEEE.Std_Logic_1164.ALL;

ENTITY top_module IS
  PORT (
    a : IN  std_logic;
    y : OUT STD_LOGIC
  );
END ENTITY top_module;

architecture RTL of TOP_MODULE is
  SIGNAL scratch : Std_Logic;  -- unused; shows that SIGNAL/signal are the same keyword
begin
  -- Write your answer on the next line. Remember the ';' at the end.

END ARCHITECTURE rtl;
