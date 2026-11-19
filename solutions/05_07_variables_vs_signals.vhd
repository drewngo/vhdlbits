library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, a, b, c : in  std_logic;
    y_var, y_sig : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  signal t : std_logic;
begin
  process(clk)
    variable v : std_logic;
  begin
    if rising_edge(clk) then
      v     := a xor b;
      t     <= a xor b;
      y_var <= v and c;
      y_sig <= t and c;
    end if;
  end process;
end architecture rtl;
