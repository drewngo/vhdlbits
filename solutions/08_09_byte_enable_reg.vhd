library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, resetn : in  std_logic;
    be          : in  std_logic_vector(1 downto 0);
    d           : in  std_logic_vector(15 downto 0);
    q           : out std_logic_vector(15 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if resetn = '0' then
        q <= (others => '0');
      else
        if be(1) = '1' then
          q(15 downto 8) <= d(15 downto 8);
        end if;
        if be(0) = '1' then
          q(7 downto 0) <= d(7 downto 0);
        end if;
      end if;
    end if;
  end process;
end architecture rtl;
