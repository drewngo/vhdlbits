library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset, a, b : in  std_logic;
    p, q             : out std_logic
  );
end entity top_module;

-- q toggles at every edge where a and b are both 1; p = q xor b.
architecture rtl of top_module is
  signal s : std_logic;
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        s <= '0';
      elsif a = '1' and b = '1' then
        s <= not s;
      end if;
    end if;
  end process;
  q <= s;
  p <= s xor b;
end architecture rtl;
