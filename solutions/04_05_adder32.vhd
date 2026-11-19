library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    a, b : in  std_logic_vector(31 downto 0);
    sum  : out std_logic_vector(31 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  signal c16 : std_logic;
begin
  u_lo: entity work.add16
    port map (a => a(15 downto 0), b => b(15 downto 0), cin => '0',
              sum => sum(15 downto 0), cout => c16);
  u_hi: entity work.add16
    port map (a => a(31 downto 16), b => b(31 downto 16), cin => c16,
              sum => sum(31 downto 16), cout => open);
end architecture rtl;
