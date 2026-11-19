library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset : in  std_logic;
    d          : in  std_logic_vector(7 downto 0);
    q          : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        q <= x"00";
      else
        q <= d;
      end if;
    end if;
  end process;
end architecture rtl;
