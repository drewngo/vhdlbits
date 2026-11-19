library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk : in  std_logic;
    d4  : in  std_logic_vector(3 downto 0);
    q4  : out std_logic_vector(3 downto 0);
    d12 : in  std_logic_vector(11 downto 0);
    q12 : out std_logic_vector(11 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  u4: entity work.reg_n
    generic map (N => 4)
    port map (clk => clk, d => d4, q => q4);
  u12: entity work.reg_n
    generic map (N => 12)
    port map (clk => clk, d => d12, q => q12);
end architecture rtl;
