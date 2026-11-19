library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, d : in  std_logic;
    q      : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  signal q1, q2 : std_logic;
begin
  u1: entity work.my_dff port map (clk => clk, d => d,  q => q1);
  u2: entity work.my_dff port map (clk => clk, d => q1, q => q2);
  u3: entity work.my_dff port map (clk => clk, d => q2, q => q);
end architecture rtl;
