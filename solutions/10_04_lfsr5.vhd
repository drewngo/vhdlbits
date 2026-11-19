library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset : in  std_logic;
    q          : out std_logic_vector(4 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  signal r : std_logic_vector(4 downto 0);
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        r <= "00001";
      else
        r <= r(0) & r(4) & (r(3) xor r(0)) & r(2) & r(1);
      end if;
    end if;
  end process;
  q <= r;
end architecture rtl;
