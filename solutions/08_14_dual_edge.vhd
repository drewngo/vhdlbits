library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, d : in  std_logic;
    q      : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  signal q_pos, q_neg : std_logic;
begin
  process(clk)
  begin
    if rising_edge(clk) then
      q_pos <= d;
    end if;
  end process;

  process(clk)
  begin
    if falling_edge(clk) then
      q_neg <= d;
    end if;
  end process;

  q <= q_pos when clk = '1' else q_neg;
end architecture rtl;
