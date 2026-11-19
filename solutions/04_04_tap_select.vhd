library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk : in  std_logic;
    d   : in  std_logic_vector(7 downto 0);
    sel : in  std_logic_vector(1 downto 0);
    q   : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  signal s1, s2, s3 : std_logic_vector(7 downto 0);
begin
  u1: entity work.my_dff8 port map (clk => clk, d => d,  q => s1);
  u2: entity work.my_dff8 port map (clk => clk, d => s1, q => s2);
  u3: entity work.my_dff8 port map (clk => clk, d => s2, q => s3);

  with sel select
    q <= d  when "00",
         s1 when "01",
         s2 when "10",
         s3 when others;
end architecture rtl;
