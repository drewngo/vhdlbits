library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, clear, load : in  std_logic;
    d                : in  std_logic_vector(7 downto 0);
    q                : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  load_p: process(clk)
  begin
    if rising_edge(clk) then
      if load = '1' then
        q <= d;
      end if;
    end if;
  end process load_p;

  clear_p: process(clk)
  begin
    if rising_edge(clk) then
      if clear = '1' then
        q <= (others => '0');
      end if;
    end if;
  end process clear_p;
end architecture rtl;
