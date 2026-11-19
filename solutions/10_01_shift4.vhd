library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, areset, load, en : in  std_logic;
    d                     : in  std_logic_vector(3 downto 0);
    q                     : out std_logic_vector(3 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  signal r : std_logic_vector(3 downto 0);
begin
  process(clk, areset)
  begin
    if areset = '1' then
      r <= "0000";
    elsif rising_edge(clk) then
      if load = '1' then
        r <= d;
      elsif en = '1' then
        r <= '0' & r(3 downto 1);
      end if;
    end if;
  end process;
  q <= r;
end architecture rtl;
