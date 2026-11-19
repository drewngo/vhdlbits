library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, reset : in  std_logic;
    a, b, c    : in  std_logic_vector(7 downto 0);
    y          : out std_logic_vector(16 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  signal s1_sum  : unsigned(8 downto 0);
  signal s1_c    : unsigned(7 downto 0);
  signal s2_prod : unsigned(16 downto 0);
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        s1_sum  <= (others => '0');
        s1_c    <= (others => '0');
        s2_prod <= (others => '0');
      else
        s1_sum  <= resize(unsigned(a), 9) + unsigned(b);
        s1_c    <= unsigned(c);
        s2_prod <= s1_sum * s1_c;
      end if;
    end if;
  end process;
  y <= std_logic_vector(s2_prod);
end architecture rtl;
