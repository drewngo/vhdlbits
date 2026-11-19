library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset, en : in  std_logic;
    q              : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  signal r : std_logic_vector(7 downto 0);
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        r <= "00000001";
      elsif en = '1' then
        r <= r(6 downto 0) & r(7);
      end if;
    end if;
  end process;
  q <= r;
end architecture rtl;
