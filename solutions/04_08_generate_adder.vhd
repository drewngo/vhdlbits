library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    a, b  : in  std_logic_vector(7 downto 0);
    cin   : in  std_logic;
    sum   : out std_logic_vector(7 downto 0);
    couts : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  signal c : std_logic_vector(8 downto 0);
begin
  c(0) <= cin;
  gen_fa: for i in 0 to 7 generate
    u_fa: entity work.full_adder
      port map (a => a(i), b => b(i), cin => c(i), s => sum(i), cout => c(i + 1));
  end generate gen_fa;
  couts <= c(8 downto 1);
end architecture rtl;
