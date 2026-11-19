library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset : in  std_logic;
    req        : in  std_logic_vector(2 downto 0);
    gnt        : out std_logic_vector(2 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  signal g : std_logic_vector(2 downto 0);
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        g <= "000";
      elsif (g and req) /= "000" then
        null;                                  -- grant held
      elsif req(0) = '1' then
        g <= "001";
      elsif req(1) = '1' then
        g <= "010";
      elsif req(2) = '1' then
        g <= "100";
      else
        g <= "000";
      end if;
    end if;
  end process;
  gnt <= g;
end architecture rtl;
