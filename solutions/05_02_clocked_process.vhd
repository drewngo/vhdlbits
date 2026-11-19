library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, a, b            : in  std_logic;
    y_conc, y_comb, y_ff : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  y_conc <= a xor b;

  process(all)
  begin
    y_comb <= a xor b;
  end process;

  process(clk)
  begin
    if rising_edge(clk) then
      y_ff <= a xor b;
    end if;
  end process;
end architecture rtl;
