library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, reset, valid : in  std_logic;
    x                 : in  std_logic_vector(7 downto 0);
    y                 : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  type hist_t is array (0 to 3) of unsigned(7 downto 0);
  signal h   : hist_t;
  signal sum : unsigned(9 downto 0);
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        h <= (others => (others => '0'));
      elsif valid = '1' then
        h <= unsigned(x) & h(0 to 2);
      end if;
    end if;
  end process;

  sum <= resize(h(0), 10) + h(1) + h(2) + h(3);
  y   <= std_logic_vector(sum(9 downto 2));
end architecture rtl;
