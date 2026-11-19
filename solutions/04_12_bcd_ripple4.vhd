library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    a, b : in  std_logic_vector(15 downto 0);
    cin  : in  std_logic;
    sum  : out std_logic_vector(15 downto 0);
    cout : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  signal c : std_logic_vector(4 downto 0);
begin
  c(0) <= cin;
  gen_digit: for i in 0 to 3 generate
    u_d: entity work.bcd_fadd
      port map (a => a(4 * i + 3 downto 4 * i), b => b(4 * i + 3 downto 4 * i), cin => c(i),
                s => sum(4 * i + 3 downto 4 * i), cout => c(i + 1));
  end generate gen_digit;
  cout <= c(4);
end architecture rtl;
