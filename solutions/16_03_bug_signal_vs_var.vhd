library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, reset : in  std_logic;
    x          : in  std_logic_vector(7 downto 0);
    total      : out std_logic_vector(11 downto 0);
    over       : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  signal acc : unsigned(11 downto 0);
begin
  process(clk)
    variable nxt : unsigned(11 downto 0);
  begin
    if rising_edge(clk) then
      if reset = '1' then
        acc  <= (others => '0');
        over <= '0';
      else
        nxt := acc + unsigned(x);
        acc <= nxt;
        if nxt >= 2048 then
          over <= '1';
        else
          over <= '0';
        end if;
      end if;
    end if;
  end process;
  total <= std_logic_vector(acc);
end architecture rtl;
